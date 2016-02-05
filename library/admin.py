# from django.forms import Textarea
from django.contrib import admin

from library.models import LibraryStock, LibraryPlate


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


admin.site.register(LibraryStock, LibraryStockAdmin)
admin.site.register(LibraryPlate, LibraryPlateAdmin)
