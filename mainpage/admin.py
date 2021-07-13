from django.contrib import admin

from .admin_actions import export_as_csv, export_forms_as_csv


admin.site.add_action(export_as_csv, 'export_selected')
admin.site.add_action(export_forms_as_csv, 'export_selected_forms')
