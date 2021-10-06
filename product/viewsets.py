from rest_framework import viewsets
from .models import *
from .serializers import *
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
import requests


# class ProductViewSet(viewsets.ModelViewSet):

    # def get_object(self, pk):
    #     return Product.objects.get(pk=pk)

    # def patch(self, request, pk):
    #     testmodel = self.get_object(pk)
    #     print(testmodel)
    #     serializer = ProductSerializer(testmodel, data=request.data,
    #                                      partial=True)  # set partial=True to update a data partially
    #     if serializer.is_valid():
    #         serializer.save()
    #         return JsonResponse(code=201, data=serializer.data)
    #     return JsonResponse(code=400, data="wrong parameters")

    # def get(self, request):
    #     queryset = Product.objects.all()
    #     serializer_class = ProductSerializer(queryset, many=True)
    #     return Response(serializer_class.data)




    # def get_object(self, pk):
    #     try:
    #         return Product.objects.get(pk=pk)
    #     except Product.DoesNotExist:
    #         raise status.HTTP_404_NOT_FOUND
    #
    # def get(self, reguest, pk, format=None):
    #     snippet = self.get_object(pk)
    #     serializer = ProductSerializer(snippet)
    #     return Response(serializer.data)





    # def patch(self, request, pk):
    #     obj = self.get_object(pk)
    #     print(obj)
    #
    #     serializer = ProductSerializer(obj, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    #     return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
