from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    # has_permission() serve method like POST/GET /api/comments/
    # has_object_permission() serve method like GET/DELETE/PATCH/PUT /api/comments/1/
    # For action with detail=False trigger has_permission()
    # For action with detail=True trigger has_permission() and has_object_permission()
    # For error, return IsObjectOwner.message by default
    message = "You do not have permission to access this object"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user