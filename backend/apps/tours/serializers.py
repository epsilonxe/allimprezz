from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from libs.tours.cost import CostItem as CostItemLib, CostScenario, CostFeasibility

from .models import Tour, TourCostItem, TourCostScenario, TourExchangeRate


def _get_exchange_rates_dict(tour):
    return {
        er.currency_code: Decimal(str(er.rate))
        for er in tour.exchange_rates.all()
    }


class TourCostItemSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()
    total_cost_thb = serializers.SerializerMethodField()

    class Meta:
        model = TourCostItem
        fields = [
            'id', 'item_number', 'name', 'category', 'pay_to',
            'unit_cost', 'currency',
            'is_synced', 'notes', 'total_cost', 'total_cost_thb',
        ]

    def get_total_cost(self, obj):
        return str(Decimal(str(obj.unit_cost)) * obj.scenario.num_pax)

    def get_total_cost_thb(self, obj):
        total_local = Decimal(str(obj.unit_cost)) * obj.scenario.num_pax
        if obj.currency == 'THB':
            return str(total_local)
        rates = _get_exchange_rates_dict(obj.scenario.tour)
        rate = rates.get(obj.currency)
        if rate is None:
            return None
        return str(total_local * rate)


class TourCostItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCostItem
        fields = [
            'id', 'item_number', 'name', 'category', 'pay_to',
            'unit_cost', 'currency',
            'is_synced', 'notes',
        ]

    def validate_category(self, value):
        if value not in CostItemLib.CATEGORY_CHOICES:
            raise serializers.ValidationError(
                f"Invalid category. Must be one of: {', '.join(CostItemLib.CATEGORY_CHOICES)}"
            )
        return value


class TourCostScenarioSerializer(serializers.ModelSerializer):
    items = TourCostItemSerializer(many=True, read_only=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = TourCostScenario
        fields = [
            'id', 'label', 'num_pax', 'num_tour_leaders',
            'markup_percent', 'selling_price_per_pax', 'notes',
            'is_desired', 'items', 'summary', 'created_at', 'updated_at',
        ]

    def _to_lib(self, obj):
        exchange_rates = _get_exchange_rates_dict(obj.tour)
        scenario = CostScenario(
            num_pax=obj.num_pax,
            markup_percent=obj.markup_percent,
            selling_price_per_pax=obj.selling_price_per_pax,
            num_tour_leaders=obj.num_tour_leaders,
            exchange_rates=exchange_rates,
        )
        for item in obj.items.all():
            scenario.add_item(CostItemLib(
                name=item.name,
                category=item.category,
                unit_cost=item.unit_cost,
                currency=item.currency,
            ))
        return scenario

    def get_summary(self, obj):
        try:
            scenario = self._to_lib(obj)
            s = scenario.summary()
            del s['items']
            return s
        except ValueError as e:
            return {'error': str(e)}


class TourCostScenarioWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCostScenario
        fields = [
            'id', 'label', 'num_pax', 'num_tour_leaders',
            'markup_percent', 'selling_price_per_pax', 'notes',
            'is_desired',
        ]
        extra_kwargs = {
            'selling_price_per_pax': {'required': False},
            'markup_percent': {'required': False},
        }

    def validate_num_pax(self, value):
        if value < 1:
            raise serializers.ValidationError("Number of passengers must be at least 1.")
        return value

    def update(self, instance, validated_data):
        with transaction.atomic():
            if validated_data.get('is_desired') is True:
                instance.tour.cost_scenarios.exclude(pk=instance.pk).update(is_desired=False)
            return super().update(instance, validated_data)


class TourExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourExchangeRate
        fields = ['id', 'currency_code', 'rate']

    def validate_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Exchange rate must be positive.")
        return value


class TourListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    scenario_count = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'name', 'destination', 'duration_days',
            'start_date', 'end_date', 'status',
            'created_by', 'created_by_name', 'scenario_count',
            'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name
        return None

    def get_scenario_count(self, obj):
        return obj.cost_scenarios.count()


class TourDetailSerializer(serializers.ModelSerializer):
    cost_scenarios = TourCostScenarioSerializer(many=True, read_only=True)
    exchange_rates = TourExchangeRateSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    feasibility = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'name', 'description', 'destination', 'duration_days',
            'start_date', 'end_date', 'status',
            'created_by', 'created_by_name',
            'cost_scenarios', 'exchange_rates', 'feasibility',
            'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name
        return None

    def get_feasibility(self, obj):
        scenarios = obj.cost_scenarios.prefetch_related('items').all()
        if not scenarios:
            return None
        exchange_rates = _get_exchange_rates_dict(obj)
        feasibility = CostFeasibility(tour_name=obj.name)
        for code, rate in exchange_rates.items():
            feasibility.set_exchange_rate(code, rate)
        for sc in scenarios:
            lib_scenario = CostScenario(
                num_pax=sc.num_pax,
                label=sc.label,
                markup_percent=sc.markup_percent,
                selling_price_per_pax=sc.selling_price_per_pax,
                num_tour_leaders=sc.num_tour_leaders,
                exchange_rates=exchange_rates,
            )
            for item in sc.items.all():
                lib_scenario.add_item(CostItemLib(
                    name=item.name,
                    category=item.category,
                    unit_cost=item.unit_cost,
                    currency=item.currency,
                ))
            feasibility.add_scenario(lib_scenario)
        try:
            result = feasibility.comparison()
            for s in result['scenarios']:
                del s['items']
            return result
        except ValueError as e:
            return {'error': str(e)}


class TourCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = [
            'id', 'name', 'description', 'destination', 'duration_days',
            'start_date', 'end_date', 'status',
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TourUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = [
            'name', 'description', 'destination', 'duration_days',
            'start_date', 'end_date', 'status',
        ]

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        duration = data.get('duration_days', getattr(self.instance, 'duration_days', None))

        if start and end:
            data['duration_days'] = (end - start).days + 1
        elif start and duration:
            data['end_date'] = start + timedelta(days=duration - 1)
        elif end and duration:
            data['start_date'] = end - timedelta(days=duration - 1)
        return data
