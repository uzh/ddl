import csv
import json

from io import StringIO

from django.http import StreamingHttpResponse, HttpResponse


def keyset_pagination_iterator(input_queryset, batch_size=500):
    all_queryset = input_queryset.order_by("pk")
    last_pk = None
    while True:
        queryset = all_queryset
        if last_pk is not None:
            queryset = all_queryset.filter(pk__gt=last_pk)
        queryset = queryset[:batch_size]
        for row in queryset:
            last_pk = row.pk
            yield row
        if not queryset:
            break


def export_as_csv(modeladmin, request, queryset):
    def rows(queryset):

        csvfile = StringIO()
        csvwriter = csv.writer(csvfile)
        columns = [field.name for field in modeladmin.model._meta.fields]

        def read_and_flush():
            csvfile.seek(0)
            data = csvfile.read()
            csvfile.seek(0)
            csvfile.truncate()
            return data

        header = False

        if not header:
            header = True
            csvwriter.writerow(columns)
            yield read_and_flush()

        for row in keyset_pagination_iterator(queryset):
            csvwriter.writerow(getattr(row, column) for column in columns)
            yield read_and_flush()

    response = StreamingHttpResponse(rows(queryset), content_type="text/csv")
    response["Content-Disposition"] = (
            "attachment; filename=%s.csv" % modeladmin.model.__name__
    )

    return response


def export_forms_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response["Content-Disposition"] = (
            "attachment; filename=%s.csv" % modeladmin.model.__name__
    )

    csvwriter = csv.writer(response)
    columns = [field.name for field in modeladmin.model._meta.fields]

    if 'data' in columns:

        form_fields = []
        for submission in queryset.only('data', 'sent_at').iterator():
            json_data_row = json.loads(submission.data)

            for entry in json_data_row:
                if entry['name'] not in form_fields:
                    form_fields.append(entry['name'])

        form_fields.append('sent_at')
        csvwriter.writerow(form_fields)

        for submission in queryset.only('data').iterator():
            json_data_row = json.loads(submission.data)
            row_data = []
            for field in form_fields:
                if field == 'sent_at':
                    row_data.append(submission.sent_at)
                    next

                for entry in json_data_row:
                    if entry['name'] == field:
                        row_data.append(entry['value'])
                        break
                else:
                    row_data.append('')

            csvwriter.writerow(row_data)

    return response
