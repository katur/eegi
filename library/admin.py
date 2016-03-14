# from django.forms import Textarea
from django.contrib import admin

from library.models import LibraryStock, LibraryPlate


class LibraryStockInline(admin.TabularInline):
    model = LibraryStock

    raw_id_fields = (
        'parent_stock',
        'intended_clone',
        'sequence_verified_clone',
    )

    readonly_fields = (
        'plate',
        'well',
    )

    fields = (
        'plate',
        'well',
        'parent_stock',
        'intended_clone',
        'sequence_verified_clone',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LibraryPlateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'number_of_wells',
        'screen_stage',
    )

    search_fields = (
        'id',
    )

    fields = (
        'number_of_wells',
        'screen_stage',
    )

    inlines = [LibraryStockInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(LibraryPlate, LibraryPlateAdmin)
