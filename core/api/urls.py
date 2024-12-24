from django.urls import path
from .views import GetData, NewOrder

urlpatterns = [
    path('get-data', GetData.as_view(), name = 'get-data'),
    path('new-order', NewOrder.as_view(), name = 'new-order'),
]