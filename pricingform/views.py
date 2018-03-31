from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .serializers import DeritradePricingFormViewSerializer, SGMarketsPricingFormViewSerializer
# Create your views here.


class DeritradePricingFormView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = DeritradePricingFormViewSerializer

    def get_object(self):
        pass

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'final_result': serializer.data['final_result']})


class SGMarketsPricingFormView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = SGMarketsPricingFormViewSerializer

    def get_object(self):
        pass

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'final_result': serializer.data['final_result']})
