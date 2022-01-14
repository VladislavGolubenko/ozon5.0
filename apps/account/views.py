from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
import requests
from rest_framework.generics import CreateAPIView, UpdateAPIView
from .models import User
from .serializers import UserSerializer, MeSerializer
from .permissions import IsOwnerAccount
from django.contrib.auth import password_validation

# Пока не используется, так как нет такой потребности
class UserView(CreateAPIView): 
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer#RegistrationSerializer
    queryset = User.objects.all()
    # def get(self, request):
    #     user = User.objects.all()
    #     serializer = UserSerializer(user, many=True)
    #     return Response(serializer.data)


class ResetPasswordView(APIView):


    def post(self, request, *args, **kwargs):
        
        old_password = self.request.data.get("old_password")
        new_password = self.request.data.get("new_password")
        print(old_password, new_password)
        if old_password is not None and new_password is not None:
            user = User.objects.filter(pk=self.request.user.pk).first()
            if user.check_password(old_password) is False:
                return Response(data={"old password not match current": "old password not match current"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.set_password(new_password)
                user.save()
                data = MeSerializer(user).data
                return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data={"field old_password or new_password is not find": "field old_password or new_password is not find"}, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerAccount]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # def get_object(self, pk):
    #     try:
    #         return User.objects.get(pk=pk)
    #     except User.DoesNotExist:
    #         raise Http404

    # def patch(self, request, pk):
    #     queryset = self.get_object(pk)
    #     serializer = UserSerializer(queryset, data=request.data, context={'request': request, 'pk': pk, })

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def get(self, request, pk):
    #     queryset = self.get_object(pk)
    #     serializer = MeSerializer(queryset)
    #     return Response(serializer.data)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_data = MeSerializer(
            User.objects.get(pk=self.request.user.pk)
        )

        return Response(data=user_data.data, status=status.HTTP_200_OK)