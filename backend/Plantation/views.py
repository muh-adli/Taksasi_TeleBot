from django.shortcuts import render
from django.core.serializers import serialize

## Models
from .models import MitraPlanted

# Create your views here.
def haStatement(request):
    title = "Hectare Statement"
        
    context = {
        'title': title,
    }
    return render(request, 'plantation/haStatement.html', context)

def taksasiPage(request):
    title = "Taksasi Page"
    
    qs = MitraPlanted.objects.all()

    # Convert queryset to GeoJSON
    geojson_data = serialize('geojson', qs, geometry_field='geom', fields=['plot_id', 'desa', 'dusun', 'wilayah'])

    context = {
        'title': title,
        'geojson': geojson_data,  # Pass GeoJSON to the template
    }

    return render(request, 'plantation/taksasi_home.html', context)

def taksasiTable(request):
    title = "Table Taksasi"
        
    context = {
        'title': title,
    }
    return render(request, 'plantation/taksasi_table.html', context)

def taksasiMap(request):
    title = "Map Taksasi"
        
    context = {
        'title': title,
    }
    return render(request, 'plantation/taksasi_map.html', context)
