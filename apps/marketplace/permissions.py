from rest_framework.permissions import BasePermission
from ..account.models import User

class IsOwnerMarketplace(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user==obj.user or request.user.role == User.ADMIN)
