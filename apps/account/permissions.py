from rest_framework.permissions import BasePermission
from .models import User

class IsSubscription(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'subscription' or request.user.role == 'admin')

class IsOwnerAccount(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user==obj or request.user.role == User.ADMIN)
