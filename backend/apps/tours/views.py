from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsStaffUser

from .models import Tour, TourCostItem, TourCostScenario, TourExchangeRate
from .serializers import (
    TourCostItemSerializer,
    TourCostItemWriteSerializer,
    TourCostScenarioSerializer,
    TourCostScenarioWriteSerializer,
    TourCreateSerializer,
    TourDetailSerializer,
    TourExchangeRateSerializer,
    TourListSerializer,
    TourUpdateSerializer,
)



def _replicate_synced_item(item):
    """Create copies of a synced item in all other scenarios of the same tour."""
    tour = item.scenario.tour
    other_scenarios = TourCostScenario.objects.filter(tour=tour).exclude(pk=item.scenario_id)
    for scenario in other_scenarios:
        if not TourCostItem.objects.filter(
            scenario=scenario, item_number=item.item_number, is_synced=True,
        ).exists():
            TourCostItem.objects.create(
                scenario=scenario,
                item_number=item.item_number,
                name=item.name,
                category=item.category,
                pay_to=item.pay_to,
                unit_cost=item.unit_cost,
                currency=item.currency,
                is_synced=True,
                notes=item.notes,
            )


def _populate_synced_items_from_siblings(scenario):
    """Pull all unique synced items from sibling scenarios into a freshly created scenario."""
    sibling_synced = TourCostItem.objects.filter(
        scenario__tour=scenario.tour,
        is_synced=True,
    ).exclude(scenario=scenario).order_by('item_number')

    seen_numbers = set()
    for item in sibling_synced:
        if item.item_number in seen_numbers:
            continue
        seen_numbers.add(item.item_number)
        TourCostItem.objects.create(
            scenario=scenario,
            item_number=item.item_number,
            name=item.name,
            category=item.category,
            pay_to=item.pay_to,
            unit_cost=item.unit_cost,
            currency=item.currency,
            is_synced=True,
            notes=item.notes,
        )


# --- Tour CRUD ---

class TourListView(ListAPIView):
    serializer_class = TourListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Tour.objects.select_related('created_by')
        tour_status = self.request.query_params.get('status')
        if tour_status:
            queryset = queryset.filter(status=tour_status)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class TourCreateView(CreateAPIView):
    serializer_class = TourCreateSerializer
    permission_classes = [IsStaffUser]


class TourDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return Tour.objects.select_related('created_by').prefetch_related(
            'cost_scenarios__items', 'exchange_rates',
        )

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TourUpdateSerializer
        return TourDetailSerializer


# --- Cost Scenario CRUD ---

class ScenarioListCreateView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, tour_pk):
        scenarios = TourCostScenario.objects.filter(
            tour_id=tour_pk,
        ).prefetch_related('items')
        serializer = TourCostScenarioSerializer(scenarios, many=True)
        return Response(serializer.data)

    def post(self, request, tour_pk):
        try:
            tour = Tour.objects.get(pk=tour_pk)
        except Tour.DoesNotExist:
            return Response(
                {'detail': 'Tour not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data.copy()
        if not data.get('label') and not TourCostScenario.objects.filter(tour=tour).exists():
            data['label'] = 'Default'
        serializer = TourCostScenarioWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        scenario = serializer.save(tour=tour)

        copy_from = request.data.get('copy_from')
        if copy_from:
            try:
                source = TourCostScenario.objects.get(pk=copy_from, tour=tour)
                for item in source.items.all():
                    TourCostItem.objects.create(
                        scenario=scenario,
                        item_number=item.item_number,
                        name=item.name,
                        category=item.category,
                        pay_to=item.pay_to,
                        unit_cost=item.unit_cost,
                        currency=item.currency,
                        is_synced=item.is_synced,
                        notes=item.notes,
                    )
            except TourCostScenario.DoesNotExist:
                pass
        else:
            _populate_synced_items_from_siblings(scenario)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScenarioDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return TourCostScenario.objects.filter(
            tour_id=self.kwargs['tour_pk'],
        ).prefetch_related('items')

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TourCostScenarioWriteSerializer
        return TourCostScenarioSerializer


# --- Cost Item CRUD ---

class CostItemListCreateView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, tour_pk, scenario_pk):
        items = TourCostItem.objects.filter(scenario_id=scenario_pk, scenario__tour_id=tour_pk)
        serializer = TourCostItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, tour_pk, scenario_pk):
        try:
            scenario = TourCostScenario.objects.get(pk=scenario_pk, tour_id=tour_pk)
        except TourCostScenario.DoesNotExist:
            return Response(
                {'detail': 'Scenario not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data.copy()
        if 'is_synced' not in data:
            default_scenario_id = TourCostScenario.objects.filter(
                tour_id=tour_pk,
            ).order_by('created_at').values_list('id', flat=True).first()
            data['is_synced'] = (scenario.id == default_scenario_id)
        serializer = TourCostItemWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(scenario=scenario)
        item = serializer.instance
        if item.is_synced:
            _replicate_synced_item(item)
        out = TourCostItemSerializer(item).data
        return Response(out, status=status.HTTP_201_CREATED)


class CostItemDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return TourCostItem.objects.filter(
            scenario_id=self.kwargs['scenario_pk'],
            scenario__tour_id=self.kwargs['tour_pk'],
        )

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TourCostItemWriteSerializer
        return TourCostItemSerializer

    SYNC_FIELDS = (
        'name', 'category', 'pay_to', 'unit_cost',
        'currency', 'notes',
    )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            item = self.get_object()
            if item.is_synced:
                # If is_synced was just toggled on, replicate to other scenarios
                if 'is_synced' in request.data:
                    _replicate_synced_item(item)
                # Propagate changed fields to existing synced siblings
                fields_to_sync = {
                    f: getattr(item, f) for f in self.SYNC_FIELDS
                    if f in request.data
                }
                if fields_to_sync:
                    TourCostItem.objects.filter(
                        item_number=item.item_number,
                        scenario__tour=item.scenario.tour,
                        is_synced=True,
                    ).exclude(pk=item.pk).update(**fields_to_sync)
            response.data = TourCostItemSerializer(item).data
        return response

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        if item.is_synced:
            TourCostItem.objects.filter(
                item_number=item.item_number,
                scenario__tour=item.scenario.tour,
                is_synced=True,
            ).exclude(pk=item.pk).delete()
        return super().destroy(request, *args, **kwargs)


# --- Exchange Rate CRUD ---

class ExchangeRateListCreateView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, tour_pk):
        rates = TourExchangeRate.objects.filter(tour_id=tour_pk)
        serializer = TourExchangeRateSerializer(rates, many=True)
        return Response(serializer.data)

    def post(self, request, tour_pk):
        try:
            tour = Tour.objects.get(pk=tour_pk)
        except Tour.DoesNotExist:
            return Response(
                {'detail': 'Tour not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TourExchangeRateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tour=tour)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExchangeRateDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TourExchangeRateSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return TourExchangeRate.objects.filter(tour_id=self.kwargs['tour_pk'])
