from django.contrib import admin
from experiments.models import Experiment


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


admin.site.register(Experiment, ExperimentAdmin)
