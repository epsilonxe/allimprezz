from django.urls import path

from .views import (
    CostItemDetailView,
    CostItemListCreateView,
    ExchangeRateDetailView,
    ExchangeRateListCreateView,
    ScenarioDetailView,
    ScenarioListCreateView,
    TourCreateView,
    TourDetailView,
    TourListView,
)

app_name = 'tours'

urlpatterns = [
    # Tours
    path('', TourListView.as_view(), name='tour_list'),
    path('create/', TourCreateView.as_view(), name='tour_create'),
    path('<int:pk>/', TourDetailView.as_view(), name='tour_detail'),
    # Cost Scenarios
    path('<int:tour_pk>/scenarios/', ScenarioListCreateView.as_view(), name='scenario_list_create'),
    path('<int:tour_pk>/scenarios/<int:pk>/', ScenarioDetailView.as_view(), name='scenario_detail'),
    # Cost Items
    path('<int:tour_pk>/scenarios/<int:scenario_pk>/items/', CostItemListCreateView.as_view(), name='item_list_create'),
    path('<int:tour_pk>/scenarios/<int:scenario_pk>/items/<int:pk>/', CostItemDetailView.as_view(), name='item_detail'),
    # Exchange Rates
    path('<int:tour_pk>/exchange-rates/', ExchangeRateListCreateView.as_view(), name='exchange_rate_list_create'),
    path('<int:tour_pk>/exchange-rates/<int:pk>/', ExchangeRateDetailView.as_view(), name='exchange_rate_detail'),
]
