from django.contrib import admin

from experiments.models import (Experiment, ExperimentPlate,
                                ManualScoreCode, ManualScore, DevstarScore)
from website.admin import ReadOnlyAdmin


class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'worm_strain',
        'library_well',
        'is_junk',
    )

    search_fields = (
        'id',
    )


class ExperimentPlateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'screen_stage',
        'temperature',
        'date',
        'comment',
    )

    list_filter = (
        'screen_stage',
        'temperature',
        'date',
    )

    search_fields = (
        'id',
    )


class ManualScoreCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'short_description',
        'legacy_description',
    )

    search_fields = (
        'short_description',
        'description',
        'legacy_description',
    )


class ManualScoreAdmin(admin.ModelAdmin):
    list_display = (
        'experiment',
        'scorer',
        'score_code',
    )

    list_filter = (
        'scorer',
    )

    search_fields = (
        'experiment__id',
    )


class DevstarScoreAdmin(ReadOnlyAdmin):
    list_display = (
        'experiment',
        'area_adult',
        'area_larva',
        'area_embryo',
        'count_adult',
        'count_larva',
    )

    search_fields = (
        'experiment__id',
    )


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(ExperimentPlate, ExperimentPlateAdmin)
admin.site.register(ManualScoreCode, ManualScoreCodeAdmin)
admin.site.register(ManualScore, ManualScoreAdmin)
admin.site.register(DevstarScore, DevstarScoreAdmin)
