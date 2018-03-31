from rest_framework import serializers
from rest_framework.exceptions import APIException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from collections import OrderedDict
import datetime
import time
import csv
from pricingform import products_deritrade, products_sgmarkets , constants


class DeritradePricingFormViewSerializer(serializers.Serializer):
    ProductNo = serializers.CharField(max_length=15, required = True)
    Domicile = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    Settlement = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    Currency = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    Amount = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    InitialFixing = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    FinalFixing = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    TimeType = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    SolveFor = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    Strike = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_null=True, allow_blank=True), required = False)
    Coupon = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_null=True, allow_blank=True), required = False) 
    Barrier = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_null=True, allow_blank=True), required = False) 
    Frequency = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False) 
    Commission = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_null=True, allow_blank=True), required = False) 
    CreditType = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    Listing = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    AutocallLevel = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    Tenor = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    FirstObservationIn = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    EnterTrade = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    Cap = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    Ratio = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    Floor = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    Participation = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    ProductTradedIn = serializers.ListField(
        child=serializers.CharField(max_length=15, allow_blank=True), required = False)
    UnderLying = serializers.JSONField(required=False)
 
    final_result = serializers.SerializerMethodField()

    
    def validate(self, data, *args, **kwargs):
        initial_fixing = data.get('InitialFixing')
        for date in initial_fixing:
            if date not in [str(datetime.date.today().strftime('%d/%m/%Y')), str(datetime.date.today().strftime('%d.%m.%Y'))]:
                msg = ('Initial Fixing is in a wrong format.')
                raise serializers.ValidationError({'error_msg': msg})
        return super(DeritradePricingFormViewSerializer, self).validate(data, *args, **kwargs)

    
    def get_final_result (self, validated_data):
        product_no = str(validated_data["ProductNo"])
        product_type_x = "product_type_"  + product_no
        # method is called for the desired product input
        final_result = getattr(products_deritrade, product_type_x)(validated_data, product_no)
        return final_result

    
    def create(self, validated_data):
        return validated_data



class SGMarketsPricingFormViewSerializer(serializers.Serializer):
    ProductID = serializers.ListField(
        child=serializers.CharField(max_length=30), required = False)
    Product = serializers.ListField(
        child=serializers.CharField(max_length=30), required = False)
    ProductSubtype = serializers.ListField(
        child=serializers.CharField(max_length=40), required = False)
    MaturityValue = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    SolveFor = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    Currency = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    NotionalAmount = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    RemunerationMode = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    UpfrontFee = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    SettlementType = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    Strike = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    BarrierType = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    KIBarrier = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    RecallStartAtPeriod = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    RecallThreshold = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    ObservationFrequency = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    CouponBarrier = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    CouponDefinitionType = serializers.ListField(
        child=serializers.CharField(max_length=15), required = False)
    UnderLying = serializers.JSONField(required=False)

    final_result = serializers.SerializerMethodField()

    
    def validate(self, data, *args, **kwargs):
        return super(SGMarketsPricingFormViewSerializer, self).validate(data, *args, **kwargs)

    def get_final_result(self, validated_data):
        # product_id = str(validated_data["ProductID"])
        # product_subtype = constants.SGMarkets[product_id]
        # final_result = getattr(products_sgmarkets, product_subtype)(validated_data, product_subtype)
        final_result = products_sgmarkets.automate_sgmarkets_forms(validated_data)
        return final_result
    
    def create(self, validated_data):
        return validated_data        