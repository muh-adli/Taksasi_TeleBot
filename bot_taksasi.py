import os
import hashlib
from urllib.parse import urlparse
from dotenv import load_dotenv

import psycopg2
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Load environment variables
load_dotenv()
LocalPostgres = urlparse(os.getenv("DATABASE_URL"))

# Database connection function
def connect_to_db():
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port="5432",
        )
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# Check if the plot exists in the gis_plot table
def check_plot_existence(plot_id):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM taksasi.gis_plot WHERE plot_id = %s;", (plot_id,))
                result = cur.fetchone()
                return result and result[0] > 0
        except Exception as e:
            print(f"Failed to check plot existence: {e}")
        finally:
            conn.close()
    return False

# Insert data into taksasi_rec with specific columns
def insert_sample_data(plot_id, pkp, samples):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO taksasi.taksasi_rec (
                        plot_id, pkp,
                        s1_batang, s1_berat, s1_tinggi,
                        s2_batang, s2_berat, s2_tinggi,
                        s3_batang, s3_berat, s3_tinggi,
                        s4_batang, s4_berat, s4_tinggi
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                values = (plot_id, pkp, *sum(samples, ()))
                cur.execute(query, values)
                conn.commit()
                return True
        except Exception as e:
            print(f"Failed to insert data: {e}")
        finally:
            conn.close()
    return False

# Dictionary to map user replies to actions
USER_ACTIONS = {
    "1": "Cek plot detail",
    "2": "Cek plot taksasi",
    "3": "Cek progress taksasi",
    "0": "Input data taksasi",
}

# Conversation stages
USERNAME, PASSWORD, MENU, PLOT_ID, PKP_INPUT, SAMPLE_INPUT, REVIEW_DATA = range(7)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Selamat datang! Silakan masukkan username Anda:")
    return USERNAME

# Handle username input
async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text.strip()
    context.user_data["username"] = username
    await update.message.reply_text("Terima kasih! Sekarang masukkan password Anda:")
    return PASSWORD

# Handle password input and verify
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()
    username = context.user_data["username"]

    if verify_user(username, password):
        await update.message.reply_text(f"Login sukses! Selamat datang, {username}.")
        return await display_menu(update, context)
    else:
        await update.message.reply_text("Username atau password salah. Silakan coba lagi.")
        return ConversationHandler.END

# Display menu after successful login
async def display_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["1", "2", "3", "0"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Pilih menu dalam bot taksasi:\n"
        "1: Cek plot detail\n"
        "2: Cek plot taksasi\n"
        "3: Cek progress taksasi\n"
        "0: Input data taksasi\n",
        reply_markup=markup,
    )
    return MENU

# Handle menu selection
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text.strip()

    if user_response in USER_ACTIONS:
        action = USER_ACTIONS[user_response]
        await update.message.reply_text(action)

        if user_response in ["1", "2"]:
            await update.message.reply_text("Masukkan Plot ID yang ingin dilakukan pengecekan:")
            return PLOT_ID
        elif user_response == "3":
            # Fetch and display progress taksasi
            await update.message.reply_text("Mengambil progress taksasi...")
            data = get_progress_taksasi()
            if data:
                await update.message.reply_text(f"Progress taksasi: {data}")
            else:
                await update.message.reply_text("Tidak ada data progress.")
            return ConversationHandler.END
        elif user_response == "0":
            await update.message.reply_text("Masukkan Plot ID untuk memulai input data taksasi:")
            return PLOT_ID
    else:
        await update.message.reply_text("Pilihan tidak valid. Silakan pilih 1, 2, 3, atau 0.")
        return ConversationHandler.END

# Handle Plot ID input
async def handle_plot_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    plot_id = update.message.text.strip()
    if check_plot_existence(plot_id):
        context.user_data["plot_id"] = plot_id
        await update.message.reply_text("Masukkan nilai PKP:")
        return PKP_INPUT
    else:
        await update.message.reply_text(f"Plot ID {plot_id} tidak ditemukan.")
        return ConversationHandler.END

# Handle PKP input
async def handle_pkp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pkp = update.message.text.strip()
    context.user_data["pkp"] = pkp
    context.user_data["samples"] = []  # Prepare to store all samples

    await update.message.reply_text("Masukkan data Sample 1 (format: batang,berat,tinggi):")
    return SAMPLE_INPUT

# Handle sample inputs
async def handle_sample_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        sample_data = [float(x.strip()) for x in update.message.text.split(",")]
        if len(sample_data) != 3:
            raise ValueError("Data harus dalam format: batang,berat,tinggi")

        context.user_data["samples"].append(tuple(sample_data))

        # Check if we need more samples
        if len(context.user_data["samples"]) < 4:
            await update.message.reply_text(
                f"Masukkan data Sample {len(context.user_data['samples']) + 1} (format: batang,berat,tinggi):"
            )
            return SAMPLE_INPUT
        else:
            # Review all collected data
            pkp = context.user_data["pkp"]
            samples = context.user_data["samples"]
            sample_text = "\n".join(
                [f"Sample {i+1}: batang={s[0]}, berat={s[1]}, tinggi={s[2]}" for i, s in enumerate(samples)]
            )
            await update.message.reply_text(
                f"PKP: {pkp}\nSamples:\n{sample_text}\n\nKetik 'ya' untuk konfirmasi atau 'tidak' untuk mengulang."
            )
            return REVIEW_DATA
    except Exception as e:
        await update.message.reply_text(f"Error: {e}. Coba lagi dengan format: batang,berat,tinggi.")
        return SAMPLE_INPUT

# Handle review and confirmation
async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirmation = update.message.text.strip().lower()
    if confirmation == "ya":
        plot_id = context.user_data["plot_id"]
        pkp = context.user_data["pkp"]
        samples = context.user_data["samples"]

        if insert_sample_data(plot_id, pkp, samples):
            await update.message.reply_text("Semua data berhasil disimpan.")
        else:
            await update.message.reply_text("Gagal menyimpan data ke database.")
        return MENU
    else:
        await update.message.reply_text("Data direset. Mulai dari awal.")
        return PLOT_ID

# Verify user credentials in the database
def verify_user(username, password):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT pass FROM taksasi.user_table WHERE nama = %s;", (username,))
                result = cur.fetchone()
                if result:
                    stored_password = result[0]
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    return hashed_password == stored_password
        except Exception as e:
            print(f"Failed to verify user: {e}")
        finally:
            conn.close()
    return False

# Fetch progress taksasi from the database
def get_progress_taksasi():
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT progress FROM taksasi_progress;")
                return cur.fetchall()
        except Exception as e:
            print(f"Failed to fetch progress taksasi: {e}")
        finally:
            conn.close()
    return None

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operasi dibatalkan.")
    return ConversationHandler.END

# Main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TG_BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response)],
            PLOT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plot_id)],
            PKP_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pkp)],
            SAMPLE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sample_input)],
            REVIEW_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
