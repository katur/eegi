from django.contrib import admin


class ReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return ([field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many])
