from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.author


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author