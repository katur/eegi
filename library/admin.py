# from django.forms import Textarea
# from django.db import models
from django.contrib import admin
from library.models import LibraryPlate, LibraryWell, LibrarySequencing


class LibraryPlateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'screen_stage',
        'number_of_wells',
    )

    list_filter = ('screen_stage', 'number_of_wells',)

    search_fields = ('id',)

    # No fields editable through admin interface
    readonly_fields = ('id', 'screen_stage', 'number_of_wells',)


class LibraryWellAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'plate',
        'well',
        'intended_clone',
        'parent_library_well',
    )

    list_filter = ('plate',)

    search_fields = ('plate', 'intended_clone',)

    # No fields editable through admin interface
    readonly_fields = ('id', 'plate', 'well', 'intended_clone',
                       'parent_library_well')


class LibrarySequencingAdmin(admin.ModelAdmin):
    list_display = (
        'source_library_well',
        'sample_plate_name',
        'sample_tube_number',
        'genewiz_tracking_number',
        'genewiz_tube_label',
    )

    list_filter = ('sample_plate_name', 'genewiz_tracking_number',)

    search_fields = ('source_library_well',)

    # No fields editable through admin interface
    readonly_fields = ('source_library_well', 'library_plate_copy_number',
                       'sample_plate_name', 'sample_tube_number',
                       'genewiz_tracking_number', 'genewiz_tube_label',
                       'sequence', 'ab1_filename',
                       'quality_score', 'crl', 'qv20plus',
                       'si_a', 'si_c', 'si_g', 'si_t',)
    '''
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 4, 'cols': 40, 'size': 20
            })},
    }
    '''


admin.site.register(LibraryPlate, LibraryPlateAdmin)
admin.site.register(LibraryWell, LibraryWellAdmin)
admin.site.register(LibrarySequencing, LibrarySequencingAdmin)
