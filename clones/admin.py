from django.contrib import admin
from utils.admin import ReadOnlyAdmin
from clones.models import Clone


class CloneAdmin(ReadOnlyAdmin):
    list_display = (
        'id',
    )

admin.site.register(Clone, CloneAdmin)
