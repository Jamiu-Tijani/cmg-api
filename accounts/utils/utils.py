import re
from collections import OrderedDict
from typing import Dict, List, Union

from django.utils.encoding import force_str

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from datetime import datetime


class CustomPagination(PageNumberPagination):
    page_size = 8

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "data": data,
            }
        )

    def get_link_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


class ResponseManager:
    """Utility class that abstracts how we create a DRF response"""

    @staticmethod
    def handle_response(
        data: Dict = None, errors: Dict = None, status: int = 200, message: str = ""
    ) -> Response:
        if data is None:
            data = {}
        if errors is None:
            errors = {}
        if errors:
            return Response(
                {"errors": errors, "message": message, "data": data}, status=status
            )
        return Response({"data": data, "message": message}, status=status)

    @staticmethod
    def handle_paginated_response(
        paginator_instance: PageNumberPagination = PageNumberPagination(), data=None
    ) -> Response:
        if data is None:
            data = {}
        return paginator_instance.get_paginated_response(data)

    @staticmethod
    def handle_dict_paginated_response(
        paginator_instance: PageNumberPagination = PageNumberPagination(), data=None
    ) -> Response:
        if data is None:
            data = {}
        return paginator_instance.get_link_paginated_response(data)

    @staticmethod
    def paginate_response(
        queryset, request, serializer_=None, page_size=10, paginator=CustomPagination
    ):
        paginator_instance = paginator()
        paginator_instance.page_size = page_size
        if not serializer_:
            return ResponseManager.handle_paginated_response(
                paginator_instance,
                paginator_instance.paginate_queryset(queryset, request),
            )
        return ResponseManager.handle_paginated_response(
            paginator_instance,
            serializer_(
                paginator_instance.paginate_queryset(queryset, request), many=True
            ).data,
        )

    @staticmethod
    def paginate_dict_response(
        result, request, page_size=10, paginator=CustomPagination
    ):
        paginator_instance = paginator()
        queryset = tuple(result.items())
        paginator_instance.page_size = page_size
        return ResponseManager.handle_dict_paginated_response(
            paginator_instance, paginator_instance.paginate_queryset(queryset, request)
        )

    @staticmethod
    def paginate_list_response(
        result, request, page_size=10, paginator=CustomPagination
    ):
        paginator_instance = paginator()
        queryset = result
        paginator_instance.page_size = page_size
        return ResponseManager.handle_dict_paginated_response(
            paginator_instance, paginator_instance.paginate_queryset(queryset, request)
        )
