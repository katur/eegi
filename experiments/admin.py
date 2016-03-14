from django.contrib import admin

from experiments.models import (Experiment, ExperimentPlate,
                                ManualScoreCode)


class ExperimentInline(admin.TabularInline):
    model = Experiment

    raw_id_fields = (
        'library_stock',
    )

    readonly_fields = (
        'plate',
        'well',
    )

    fields = (
        'plate',
        'well',
        'worm_strain',
        'library_stock',
        'is_junk',
        'comment',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ExperimentPlateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
    )

    search_fields = (
        'id',
    )

    fields = (
        'temperature',
        'date',
        'comment',
    )

    inlines = [ExperimentInline]

    def has_add_permission(self, request):
        return False


class ManualScoreCodeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'short_description',
        'description',
        'legacy_description',
    )

    search_fields = (
        'short_description',
        'description',
        'legacy_description',
    )

    readonly_fields = (
        'id',
    )

    fields = (
        'id',
        'short_description',
        'description',
        'legacy_description',
    )


admin.site.register(ExperimentPlate, ExperimentPlateAdmin)
admin.site.register(ManualScoreCode, ManualScoreCodeAdmin)
