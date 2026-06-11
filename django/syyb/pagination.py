from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    自定义分页器
    - 默认每页20条，兼顾性能与展示效果
    - 支持客户端通过 page_size 参数自定义（最大200条）
    - 不再支持 page_size=0 不分页，防止大数据量拖垮接口
    """
    page_size = 14
    page_size_query_param = "page_size"
    max_page_size = 200

    def paginate_queryset(self, queryset, request, view=None):
        # 兼容性处理：如果传了 page_size=0，视为使用默认分页
        if request.query_params.get(self.page_size_query_param) == '0':
            return super().paginate_queryset(queryset, request, view)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)
