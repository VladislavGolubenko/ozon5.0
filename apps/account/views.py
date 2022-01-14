from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
import requests
from rest_framework.generics import CreateAPIView, UpdateAPIView
from .models import User
from .serializers import UserSerializer, RegistrationSerializer, MeSerializer
from .permissions import IsOwnerAccount


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
        print(self.request.user)
        password = self.request.data.get("password")
        if password is not None:
            print(password)
            user = User.objects.filter(pk=self.request.user.pk).first()
            user.set_password(password)
            user.save()
            data = MeSerializer(user).data
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data={"field password is not find": "field password is not find"}, status=status.HTTP_200_OK)


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