from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Transform

class MitraPlanted(models.Model):
    id = models.AutoField(primary_key=True)
    plot_id = models.CharField(max_length=50)
    geom = models.MultiPolygonField(srid=32750)
    desa = models.TextField(blank=True, null=True)
    dusun = models.TextField(blank=True, null=True)
    wilayah = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mitra_planted'

    @property
    def geom_wgs(self):
        """Returns geometry transformed to SRID 4326 (WGS 84)."""
        return MitraPlanted.objects.annotate(geom_wgs=Transform('geom', 4326)).get(id=self.id).geom_wgs
    
class ViewTaksasiHasil(models.Model):
    plot_id = models.TextField(primary_key=True)
    petani = models.TextField(blank=True, null=True)
    luas = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    var = models.TextField(blank=True, null=True)
    kategori = models.TextField(blank=True, null=True)
    kategori_grup = models.TextField(blank=True, null=True)
    mt = models.TextField(blank=True, null=True)
    plant_date = models.DateField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    umur_taksasi = models.IntegerField(blank=True, null=True)
    umur_ditebang = models.IntegerField(blank=True, null=True)
    umur_delta = models.IntegerField(blank=True, null=True)
    juring = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    pkp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s1_batang = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s1_berat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s1_tinggi = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s2_batang = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s2_berat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s2_tinggi = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s3_batang = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s3_berat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    s3_tinggi = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rata_batang = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    rata_berat = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    rata_tinggi = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    tebang_tinggi = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    tch = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    tonase = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'view_taksasi_hasil'

class MitraPerawatan2025(models.Model):
    plot_id = models.CharField(unique=True, max_length=50)
    spraying_status = models.BooleanField(blank=True, null=True)
    spraying_date = models.DateField(blank=True, null=True)
    spraying_date_input = models.DateField(blank=True, null=True)
    fertilizing_status = models.BooleanField(blank=True, null=True)
    fertilizing_date = models.DateField(blank=True, null=True)
    fertilizing_date_input = models.DateField(blank=True, null=True)
    klentek_status = models.BooleanField(blank=True, null=True)
    klentek_date = models.DateField(blank=True, null=True)
    klentek_date_input = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '2025_mitra_perawatan'