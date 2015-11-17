# from django.forms import Textarea
# from django.db import models
from django.contrib import admin

from library.models import LibraryStock, LibraryPlate, LibrarySequencing
from website.admin import ReadOnlyAdmin


class LibraryStockAdmin(ReadOnlyAdmin):
    list_display = (
        'id',
        'parent_stock',
        'intended_clone',
    )

    search_fields = ('id', 'plate', 'intended_clone',)


class LibraryPlateAdmin(ReadOnlyAdmin):
    list_display = (
        'id',
        'number_of_wells',
        'screen_stage',
    )

    list_filter = ('screen_stage', 'number_of_wells',)

    search_fields = ('id',)


class LibrarySequencingAdmin(ReadOnlyAdmin):
    list_display = (
        'source_stock',
        'sample_plate_name',
        'sample_tube_number',
        'genewiz_tracking_number',
        'genewiz_tube_label',
    )

    list_filter = ('sample_plate_name', 'genewiz_tracking_number',)

    search_fields = ('source_stock',)

    '''
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 4, 'cols': 40, 'size': 20
            })},
    }
    '''


admin.site.register(LibraryStock, LibraryStockAdmin)
admin.site.register(LibraryPlate, LibraryPlateAdmin)
admin.site.register(LibrarySequencing, LibrarySequencingAdmin)
