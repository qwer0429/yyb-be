from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 50  # 每页显示的记录数
    page_size_query_param = "page_size"  # 允许客户端通过参数指定每页大小
    max_page_size = 2000  # 每页最大记录数
    
    def paginate_queryset(self, queryset, request, view=None):
        # 如果 page_size=0，返回全部数据不分页
        if request.query_params.get(self.page_size_query_param) == '0':
            self._return_all = True
            self._all_data = list(queryset)
            return self._all_data
        self._return_all = False
        return super().paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):
        # 如果返回全部数据，构造统一的分页响应格式
        if getattr(self, '_return_all', False):
            return Response({
                'count': len(data),
                'next': None,
                'previous': None,
                'results': data,
            })
        return super().get_paginated_response(data)
