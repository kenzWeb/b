from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    """пагинация"""
    page_size = 5
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'pagination': {
                'total': self.page.paginator.num_pages,
                'current': self.page.number,
                'per_page': self.page_size
            }
        })