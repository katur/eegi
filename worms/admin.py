from django.contrib import admin

from worms.models import WormStrain


class WormStrainAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'genotype',
        'gene',
        'allele',
        'permissive_temperature',
        'restrictive_temperature',
    )

    list_filter = ('permissive_temperature', 'restrictive_temperature')

admin.site.register(WormStrain, WormStrainAdmin)
