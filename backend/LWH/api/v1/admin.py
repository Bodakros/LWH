from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe

# Admin panel configuration
admin.site.site_header = _("LWH - Logistics Warehouse Management")
admin.site.site_title = _("LWH Admin")
admin.site.index_title = _("Platform Management")


# Base admin class for all models in the project
class LWHBaseAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if hasattr(self.model, 'created_at') and 'created_at' not in list_display:
            list_display.append('created_at')
        if hasattr(self.model, 'updated_at') and 'updated_at' not in list_display:
            list_display.append('updated_at')
        return list_display

    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request) or [])
        if hasattr(self.model, 'created_at') and 'created_at' not in list_filter:
            list_filter.append('created_at')
        if hasattr(self.model, 'is_active') and 'is_active' not in list_filter:
            list_filter.append('is_active')
        return list_filter

    def save_model(self, request, obj, form, change):
        if not change and hasattr(obj, 'created_by') and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Admin class for models with images
class LWHImageAdmin(LWHBaseAdmin):
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" />')
        return _("No image")

    image_preview.short_description = _("Preview")



# Helper function for automatic model registration
def auto_register_models(models_module, admin_class=None, exclude=None):
    if admin_class is None:
        admin_class = LWHBaseAdmin

    exclude = exclude or []

    for name in dir(models_module):
        obj = getattr(models_module, name)

        if not isinstance(obj, type) or name in exclude:
            continue

        from django.db.models import Model
        if issubclass(obj, Model) and obj.__module__ == models_module.__name__:
            admin.site.register(obj, admin_class)
