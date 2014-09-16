from django.contrib import admin
from clones.models import Clone


class CloneAdmin(admin.ModelAdmin):
    list_display = (
        'id',
    )

admin.site.register(Clone, CloneAdmin)
