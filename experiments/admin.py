from django.contrib import admin
from experiments.models import Experiment


class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'worm_strain',
        'clone_plate',
        'temperature',
        'date',
        'is_junk',
        'comment',
    )

    list_filter = (
        'worm_strain',
        'clone_plate',
        'temperature',
        'date',
        'is_junk'
    )


admin.site.register(Experiment, ExperimentAdmin)
