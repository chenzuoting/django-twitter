from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(request_attr='query_params', params=None):
    """
    When use @required_params(params=['some_param']),
    This required_params function return a decorator function，this decorator function is
    wrapped by @required_params view_func
    """

    # For better practise, argument list of a function cannot be mutable
    if params is None:
        params = []

    def decorator(view_func):
        """
        Decorator uses wraps to get arguments from view_func and pass to _wrapped_view.
        Instance here is self in view_func
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            data = getattr(request, request_attr)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            # After checking, call view_func in @required_params
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator
