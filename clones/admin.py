from django.contrib import admin

from clones.models import Clone
from utils.admin import ReadOnlyAdmin


class CloneAdmin(ReadOnlyAdmin):
    list_display = (
        'id',
    )

admin.site.register(Clone, CloneAdmin)
