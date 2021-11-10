from rest_framework.permissions import BasePermission


class IsSubscription(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'subscription')