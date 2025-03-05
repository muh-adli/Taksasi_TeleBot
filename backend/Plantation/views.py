from django.shortcuts import render
from django.core.serializers import serialize
from django.db import connection  # Import the connection object
from django.db.models import F, OuterRef, Subquery
from django.contrib.gis.db.models import Func
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Transform

## Models
from .models import (
    MitraPlanted,
    ViewTaksasiHasil,
)

import json

# Create your views here.
def haStatement(request):
    title = "Hectare Statement"
        
    context = {
        'title': title,
    }
    return render(request, 'plantation/haStatement.html', context)

def taksasiPage(request):
    title = "Taksasi Page"
    
    sql = """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'id', v.plot_id,
                    'geometry', CASE 
                                WHEN m.geom IS NOT NULL 
                                THEN ST_AsGeoJSON(ST_Transform(m.geom, 4326))::json
                                ELSE NULL
                                END,
                    'properties', json_build_object(
                        'luas', v.luas,
                        'tch', v.tch,
                        'tonase', v.tonase
                    )
                )
            )
        ) AS geojson
        FROM view_taksasi_hasil v
        LEFT JOIN mitra_planted m ON v.plot_id = m.plot_id;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        # Fetch the single row returned by the aggregate query.
        row = cursor.fetchone()
        # The first (and only) column is our GeoJSON object.
        # Depending on your PostgreSQL adapter, it may already be a string.
        geojson_result = row[0] if row and row[0] else {}
    
    # If it's not a string, convert it to one.
    if not isinstance(geojson_result, str):
        geojson_str = json.dumps(geojson_result)
    else:
        geojson_str = geojson_result
    
    print(geojson_str)

    context = {
        'title': title,
        'geojson': geojson_str,  # Pass GeoJSON string to the template.
    }
    
    # qs = MitraPlanted.objects.all()
    # Convert queryset to GeoJSON
    # geojson_data = serialize('geojson', qs, geometry_field='geom', fields=['plot_id', 'petani', 'luas', 'dusun', 'desa'])
    # geojson_data = serialize('geojson', qs, geometry_field='geom', fields=['plot_id', 'luas', 'tch', 'tonase'])

    # print(geojson_data)

    # context = {
    #     'title': title,
    #     'geojson': geojson_data,  # Pass GeoJSON to the template
    # }

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

def perawatanHome(request):
    title = "Perawatan Home"
        
    context = {
        'title': title,
    }
    return render(request, 'plantation/perawatan_home.html', context)
