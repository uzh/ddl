import csv

from ddm.datadonation.models import DataDonation
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse

from .models import User


class ExportCsvMixin:
    def export_as_csv(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:

        meta = self.model._meta  # noqa: SLF001
        field_names = ["project", "blueprint", "participant", "time_submitted",
                       "consent", "status"]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class DataDonations(admin.ModelAdmin, ExportCsvMixin):
    """
    Provides an overview of data donations.
    """
    list_display = ["project", "blueprint", "participant", "time_submitted",
                    "consent", "status", "external_id"]
    list_filter = ["project"]
    actions = ["export_as_csv"]

    def external_id(self, profile: DataDonation) -> str:
        return profile.participant.external_id

    def has_add_permission(
            self,
            request: HttpRequest,
            obj: Model | None = None
    ) -> bool:
        return False


admin.site.register(User, UserAdmin)
admin.site.register(DataDonation, DataDonations)
