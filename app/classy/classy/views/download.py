from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit
import csv

from classy.views.common import helper, shared

#Download search results from the search function
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
def download(request):
    if not request.method == 'POST':
            return redirect('classy:home')

    queryset = helper.filter_results(request, request.POST)
    queryset = queryset.order_by('datasource', 'schema', 'table', 'column')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="classification_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Application', 'Classification', 'Protected Series', 'Datasource', 'Schema', 'Table', 'Column', 'Created', 'Creator', 'State', 'Masking instructions', 'Notes'])
   
    for tuple in queryset:
        if tuple.owner is not None:
            app = tuple.owner.acronym
        else:
            app = None
        writer.writerow([app, translate[tuple.classification], translate[tuple.protected_type], tuple.datasource, tuple.schema, tuple.table, tuple.column, tuple.created, tuple.creator.first_name, state_translate[tuple.state], tuple.masking, tuple.notes])
    return response
