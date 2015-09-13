from django.contrib import admin

from clones.models import Clone
from website.admin import ReadOnlyAdmin


class CloneAdmin(ReadOnlyAdmin):
    list_display = (
        'id',
    )

admin.site.register(Clone, CloneAdmin)
