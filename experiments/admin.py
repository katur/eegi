from django.contrib import admin
from experiments.models import Experiment, ManualScoreCode, ManualScore


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
        'library_plate',
    )

    search_fields = (
        'id',
        'worm_strain__id',
        'library_plate__id',
    )


class ManualScoreCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'short_description',
        'description',
    )

    search_fields = (
        'short_description',
        'description',
    )


class ManualScoreAdmin(admin.ModelAdmin):
    list_display = (
        'score_code',
        'scorer',
        'experiment',
        'well',
    )

    list_filter = (
        'experiment__worm_strain',
        'score_code',
        'scorer',
    )

    search_fields = (
        'experiment__id',
        'experiment__worm_strain',
    )


admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(ManualScoreCode, ManualScoreCodeAdmin)
admin.site.register(ManualScore, ManualScoreAdmin)
