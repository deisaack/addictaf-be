from rest_framework import pagination

__all__ = ['AdictAFPagination']

class AdictAFPagination(pagination.LimitOffsetPagination):
    max_limit = 50
    min_limit = 1
    min_offset = 1

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                return pagination._positive_int(
                    request.query_params[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError) as e:
                pass

        return self.default_limit
