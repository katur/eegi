from django.contrib import admin

from experiments.models import (Experiment, ManualScoreCode, ManualScore,
                                DevstarScore)
from website.admin import ReadOnlyAdmin


class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'worm_strain',
        'library_plate',
        'temperature',
        'date',
        'is_junk',
        'comment',
    )

    list_filter = (
        'is_junk',
        'date',
        'temperature',
        'worm_strain',
    )

    search_fields = (
        'id',
        'library_plate__id',
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
        'well',
        'scorer',
        'score_code',
    )

    list_filter = (
        'scorer',
        'timestamp',
    )

    search_fields = (
        'experiment__id',
    )


class DevstarScoreAdmin(ReadOnlyAdmin):
    list_display = (
        'experiment',
        'well',
        'area_adult',
        'area_larva',
        'area_embryo',
        'count_adult',
        'count_larva',
    )

    list_filter = (
        'experiment__worm_strain',
    )

    search_fields = (
        'experiment__id',
        'experiment__worm_strain',
    )


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(ManualScoreCode, ManualScoreCodeAdmin)
admin.site.register(ManualScore, ManualScoreAdmin)
admin.site.register(DevstarScore, DevstarScoreAdmin)
