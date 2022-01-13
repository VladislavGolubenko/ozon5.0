from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
import requests
from rest_framework.generics import CreateAPIView
from .models import User
from .serializers import UserSerializer, RegistrationSerializer

# Пока не используется, так как нет такой потребности
class UserView(CreateAPIView): 
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer#RegistrationSerializer
    queryset = User.objects.all()
    # def get(self, request):
    #     user = User.objects.all()
    #     serializer = UserSerializer(user, many=True)
    #     return Response(serializer.data)




class UserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def patch(self, request, pk):
        queryset = self.get_object(pk)
        serializer = UserSerializer(queryset, data=request.data, context={'request': request, 'pk': pk, })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = UserSerializer(queryset)
        return Response(serializer.data)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_data = UserSerializer(
            User.objects.get(pk=self.request.user.pk)
        )

        return Response(data=user_data.data, status=status.HTTP_200_OK)