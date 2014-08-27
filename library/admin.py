from django.contrib import admin
from library.models import LibraryPlate


class LibraryPlateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'screen_stage',
        'number_of_wells',
    )

    list_filter = ('screen_stage', 'number_of_wells')

    search_fields = (
        'id',
    )

admin.site.register(LibraryPlate, LibraryPlateAdmin)
