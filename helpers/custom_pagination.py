from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response

class PageCountPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            # 'next': self.get_next_link(),
            # 'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

class BigPageCountPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            # 'next': self.get_next_link(),
            # 'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
