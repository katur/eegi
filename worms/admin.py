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

    list_filter = (
        'permissive_temperature',
        'restrictive_temperature',
    )

    fields = (
        'genotype',
        'gene',
        'allele',
        'permissive_temperature',
        'restrictive_temperature',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(WormStrain, WormStrainAdmin)
