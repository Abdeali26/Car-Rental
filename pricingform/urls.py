from django.conf.urls import url


from rest_framework.urlpatterns import format_suffix_patterns


from . import views

urlpatterns = [
    url(r'^pricingform_deritrade/$', views.DeritradePricingFormView.as_view()),
    url(r'^pricingform_sgmarkets/$', views.SGMarketsPricingFormView.as_view()),
   ]
