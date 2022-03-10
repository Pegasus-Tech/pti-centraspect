import django_filters

from .models import InspectionItem


class InspectionItemsFilters(django_filters.FilterSet):
    due_date_start = django_filters.DateFilter(field_name='next_inspection_date', lookup_expr='gte')
    due_date_end = django_filters.DateFilter(field_name='next_inspection_date', lookup_expr='lte')

    last_date_start = django_filters.DateFilter(field_name='last_inspection_date', lookup_expr='gte')
    last_date_end = django_filters.DateFilter(field_name='last_inspection_date', lookup_expr='lte')

    expiration_start = django_filters.DateFilter(field_name='expiration_date', lookup_expr='gte')
    expiration_end = django_filters.DateFilter(field_name='expiration_date', lookup_expr='lte')

    class Meta:
        model = InspectionItem
        fields = ['inspection_type', 'inspection_interval']

    @property
    def qs(self):
        qs = super().qs
        user = getattr(self.request, 'user', None)
        print(f'Filter Request :: {user}')
        return qs.filter(account=user.account).filter(is_active=True).filter(is_deleted=False)
