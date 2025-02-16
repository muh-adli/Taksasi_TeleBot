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