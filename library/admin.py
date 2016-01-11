# from django.forms import Textarea
from django.contrib import admin

from library.models import LibraryStock, LibraryPlate, LibrarySequencing


class LibraryStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_stock', 'intended_clone',)

    search_fields = ('id', 'plate', 'intended_clone',)

    readonly_fields = ('id', 'plate', 'well',)

    raw_id_fields = ('parent_stock', 'intended_clone',
                     'sequence_verified_clone',)

    fields = ('id', 'plate', 'well', 'parent_stock',
              'intended_clone', 'sequence_verified_clone',)


class LibraryPlateAdmin(admin.ModelAdmin):
    list_display = ('id', 'number_of_wells', 'screen_stage',)

    search_fields = ('id',)

    readonly_fields = ('id',)

    fields = ('id', 'number_of_wells', 'screen_stage',)


class LibrarySequencingAdmin(admin.ModelAdmin):
    list_display = (
        'source_stock',
        'sample_plate_name',
        'sample_tube_number',
        'genewiz_tracking_number',
        'genewiz_tube_label',
    )

    list_filter = ('sample_plate_name', 'genewiz_tracking_number',)

    search_fields = ('source_stock',)


admin.site.register(LibraryStock, LibraryStockAdmin)
admin.site.register(LibraryPlate, LibraryPlateAdmin)
admin.site.register(LibrarySequencing, LibrarySequencingAdmin)
