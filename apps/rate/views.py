from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework.views import APIView

from .serializers import RateSerializer
from .models import Rate

class RatesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        rates = Rate.objects.all()
        serializer = RateSerializer(rates, many=True)
        return Response(serializer.data)


class RateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Rate.objects.get(pk=pk)
        except Rate.DoesNotExist:
            raise Http404

    def patch(self, request, pk):

        queryset = self.get_object(pk)
        serializer = RateSerializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        rate = self.get_object(pk)
        serializer = RateSerializer(rate)
        return Response(serializer.data)