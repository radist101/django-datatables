
from abc import ABCMeta, abstractmethod

from django.views.generic import View
from django.http import JsonResponse
from django.db.models.query import QuerySet
from django.core.exceptions import ImproperlyConfigured


class TableParamsMixin(object):
    """
    Class for parsing options query_strings
    """

    sort_columns = None

    @property
    def _args(self):
        return self.request.GET

    @property
    def offset(self):
        return int(self._args.get('start'))

    @property
    def limit(self):
        return int(self._args.get('length'))

    @property
    def sort_field(self):
        order_label = '-' if self.order == 'desc' else ''
        return '{}{}'.format(order_label, self.sort_columns[int(self._args['order[0][column]'])])

    @property
    def order(self):
        return self._args['order[0][dir]']

    @property
    def search_text(self):
        text = self._args['search[value]']
        if isinstance(text, int):
            text = str(text)
        return text

    @property
    def draw(self):
        return int(self._args.get('draw'))


class DataTableView(TableParamsMixin, View, metaclass=ABCMeta):

    http_method_names = ['get', 'head', 'options']

    queryset = None
    model = None

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(*args, **kwargs)

        if self.search_text:
            queryset = self.get_search_result(self.search_text, queryset)

        total = queryset.count()
        queryset = queryset.order_by(self.sort_field)[self.offset: self.limit + self.offset]

        data = [self.get_columns(query) for query in queryset]

        result = {'draw': self.draw,
                  'recordsTotal': total,
                  'recordsFiltered': total,
                  'data': data}

        return JsonResponse(result)

    @abstractmethod
    def get_columns(self, query):
        pass

    def get_search_result(self, term, queryset):
        raise NotImplementedError

    def get_queryset(self, *args, **kwargs):
        """
        Copyright from the ListView

        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )

        return queryset