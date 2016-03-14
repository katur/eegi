from django.contrib import admin

from experiments.models import (Experiment, ExperimentPlate,
                                ManualScoreCode, ManualScore)


class ExperimentInline(admin.TabularInline):
    model = Experiment

    extra = 1

    # Don't load dropdown
    raw_id_fields = ('library_stock',)

    fields = ('id', 'plate', 'well', 'worm_strain', 'library_stock',
              'is_junk', 'comment',)


class ExperimentPlateAdmin(admin.ModelAdmin):
    list_display = ('id',)

    search_fields = ('id',)

    readonly_fields = ('id',)

    fields = ('id', 'temperature', 'date', 'comment',)

    inlines = [ExperimentInline]


class ManualScoreCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_description', 'description',
                    'legacy_description',)

    search_fields = ('short_description', 'description',
                     'legacy_description',)


class ManualScoreAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'scorer', 'score_code',)

    search_fields = ('experiment__id',)

    # Don't load dropdown
    raw_id_fields = ('experiment',)


admin.site.register(ExperimentPlate, ExperimentPlateAdmin)
admin.site.register(ManualScoreCode, ManualScoreCodeAdmin)
admin.site.register(ManualScore, ManualScoreAdmin)
