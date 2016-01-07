from django.contrib import admin

from experiments.models import (Experiment, ExperimentPlate,
                                ManualScoreCode, ManualScore, DevstarScore)
from website.admin import ReadOnlyAdmin


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('id',)

    list_filter = ('worm_strain', 'is_junk',)

    search_fields = ('id',)

    raw_id_fields = ('plate', 'library_stock',)

    readonly_fields = ('id', 'plate', 'well',)

    fields = ('id', 'plate', 'well', 'worm_strain', 'library_stock',
              'is_junk', 'comment',)


class ExperimentPlateAdmin(admin.ModelAdmin):
    list_display = ('id', 'screen_stage', 'temperature', 'date',)

    search_fields = ('id',)

    readonly_fields = ('id',)

    fields = ('id', 'temperature', 'date', 'comment',)


class ManualScoreCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_description', 'description',
                    'legacy_description',)

    search_fields = ('short_description', 'description',
                     'legacy_description',)


class ManualScoreAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'scorer', 'score_code',)

    search_fields = ('experiment__id',)

    raw_id_fields = ('experiment',)


class DevstarScoreAdmin(ReadOnlyAdmin):
    list_display = ('experiment', 'area_adult', 'area_larva', 'area_embryo',
                    'count_adult', 'count_larva',)

    search_fields = ('experiment__id',)

    raw_id_fields = ('experiment',)


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(ExperimentPlate, ExperimentPlateAdmin)
admin.site.register(ManualScoreCode, ManualScoreCodeAdmin)
admin.site.register(ManualScore, ManualScoreAdmin)
admin.site.register(DevstarScore, DevstarScoreAdmin)
