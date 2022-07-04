from django.conf import settings
from django.utils.functional import cached_property
from rest_framework import pagination
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import PageNumberPagination

class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values('id').count()

# class FasterPageNumberPagination(PageNumberPagination):
#     django_paginator_class = FasterDjangoPaginator

class PageCountPagination(pagination.PageNumberPagination):
    django_paginator_class = FasterDjangoPaginator
    # @cached_property
    # def count(self):
    #     return 9999999999

    def get_paginated_response(self, data):
        return Response({
            # 'next': self.get_next_link(),
            # 'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data,
        })

class Page10Pagination(PageCountPagination):
    @cached_property
    def count(self):
        return 9999999999

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10

class Page100Pagination(pagination.PageNumberPagination):
    @cached_property
    def count(self):
        return 9999999999

    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            # 'next': self.get_next_link(),
            # 'previous': self.get_previous_link(),
            'count': self.count, #self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
