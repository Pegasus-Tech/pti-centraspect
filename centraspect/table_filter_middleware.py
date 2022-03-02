from inspection_items.models import InspectionItemFilters
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
import json


def simple_middleware(get_response):
    """
        This middleware is to manage the table filtering
        if the filter key comes through we need to set a cookie containing
        the filter options, otherwise we need check the path of the url
        and if the path is not relevant to the table path - clear the cookie
    """

    def middleware(request):
        response = get_response(request)
        if not request.user.is_anonymous:
            filter_qs = InspectionItemFilters.objects.filter(created_by=request.user)
            path = request.get_full_path()

            # Only process for not static file requests
            if 'assets/lang/' not in path:
                if request.POST and '/dashboard/inspection-items/' in path:
                    filters = {}
                    for k, v in request.POST.lists():
                        if k != 'csrfmiddlewaretoken':
                            filters[k] = v

                    if filter_qs.count() <= 0:
                        filter_obj = InspectionItemFilters()
                    else:
                        filter_obj = filter_qs.get()

                    filter_obj.filters = json.dumps(filters)
                    filter_obj.is_filtering = True
                    filter_obj.created_by = request.user
                    filter_obj.save()

                else:
                    if filter_qs.count() > 0:
                        filter_obj = filter_qs.get()
                        filter_obj.is_filtering = False
                        filter_obj.save()
        return response

    return middleware
