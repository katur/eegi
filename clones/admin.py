from django.contrib import admin
from clones.models import ClonePlate


class ClonePlateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'screen_stage',
        'number_of_wells',
    )

    list_filter = ('screen_stage', 'number_of_wells')

    search_fields = (
        'id',
    )

admin.site.register(ClonePlate, ClonePlateAdmin)
