import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse

from .models import User
from ddm.datadonation.models import DataDonation, FileUploader, DonationBlueprint


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = ['project', 'blueprint', 'participant', 'time_submitted',
                       'consent', 'status']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class DataDonations(admin.ModelAdmin, ExportCsvMixin):
    """
    Provides an overview of data donations.
    """
    list_display = ['project', 'blueprint', 'participant', 'time_submitted',
                    'consent', 'status', 'external_id']
    list_filter = ['project']
    actions = ["export_as_csv"]

    def external_id(self, profile):
        return profile.participant.external_id  # Foreign key relationship

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(DataDonation, DataDonations)
