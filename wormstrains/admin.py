from django.contrib import admin
from wormstrains.models import WormStrain


class WormStrainAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'genotype',
        'gene',
        'allele',
        'permissive_temperature',
        'restrictive_temperature',
        'on_wormbase',
    )

    list_filter = ('permissive_temperature', 'restrictive_temperature')

admin.site.register(WormStrain, WormStrainAdmin)
