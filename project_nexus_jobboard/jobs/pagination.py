
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'  # let client override, eg ?page_size=20
    max_page_size = 50  # max limit

