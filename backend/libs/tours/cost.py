from decimal import Decimal, ROUND_HALF_UP


class CostItem:
    """A single cost line item in a tour cost scenario.

    Stores a per-passenger unit cost. Total cost is computed by the
    scenario using its passenger count.
    """

    CATEGORY_CHOICES = (
        'insurance', 'visa', 'miscellaneous', 'management_fee',
        'op_ticket', 'op_expense', 'accommodation', 'activity',
        'transportation', 'other',
    )

    def __init__(self, name, category, unit_cost,
                 pay_to='', currency='THB', notes=''):
        if category not in self.CATEGORY_CHOICES:
            raise ValueError(
                f"Invalid category '{category}'. "
                f"Must be one of: {', '.join(self.CATEGORY_CHOICES)}"
            )
        if unit_cost < 0:
            raise ValueError("unit_cost must be non-negative")

        self.name = name
        self.category = category
        self.unit_cost = Decimal(str(unit_cost))
        self.pay_to = pay_to
        self.currency = currency
        self.notes = notes

    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category,
            'unit_cost': str(self.unit_cost),
            'pay_to': self.pay_to,
            'currency': self.currency,
            'notes': self.notes,
        }


class CostScenario:
    """A cost scenario for a specific number of passengers.

    Models one column group from the spreadsheet: a fixed pax count
    with its own set of cost items, totals, and per-pax breakdowns.
    Each item's total is computed as unit_cost * num_pax.
    """

    def __init__(self, num_pax, markup_percent=5, selling_price_per_pax=0,
                 num_tour_leaders=0, exchange_rates=None, notes='', label=''):
        if num_pax < 1:
            raise ValueError("num_pax must be at least 1")
        if markup_percent < 0:
            raise ValueError("markup_percent must be non-negative")
        if selling_price_per_pax < 0:
            raise ValueError("selling_price_per_pax must be non-negative")

        self.num_pax = int(num_pax)
        self.label = label
        self.markup_percent = Decimal(str(markup_percent))
        self.selling_price_per_pax = Decimal(str(selling_price_per_pax))
        self.num_tour_leaders = int(num_tour_leaders)
        self.exchange_rates = exchange_rates or {}
        self.notes = notes
        self.items = []

    def add_item(self, item):
        if not isinstance(item, CostItem):
            raise TypeError("item must be a CostItem instance")
        self.items.append(item)
        return item

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        raise IndexError(f"Item index {index} out of range")

    def _unit_cost_in_thb(self, item):
        if item.currency == 'THB':
            return item.unit_cost
        rate = self.exchange_rates.get(item.currency)
        if rate is None:
            raise ValueError(
                f"No exchange rate defined for {item.currency} to THB"
            )
        return item.unit_cost * Decimal(str(rate))

    def item_total(self, item):
        """Total cost for an item in its own currency (unit_cost * num_pax)."""
        return item.unit_cost * self.num_pax

    def item_total_thb(self, item):
        """Total cost for an item in THB (unit_cost in THB * num_pax)."""
        return self._unit_cost_in_thb(item) * self.num_pax

    @property
    def total_cost(self):
        return sum(
            (self.item_total_thb(item) for item in self.items),
            Decimal('0'),
        )

    @property
    def cost_per_pax(self):
        if self.num_pax == 0:
            return Decimal('0')
        return (self.total_cost / self.num_pax).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    @property
    def computed_selling_price_per_pax(self):
        markup = self.cost_per_pax * (self.markup_percent / Decimal('100'))
        return (self.cost_per_pax + markup).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    @property
    def effective_selling_price_per_pax(self):
        if self.selling_price_per_pax > 0:
            return self.selling_price_per_pax
        return self.computed_selling_price_per_pax

    @property
    def total_revenue(self):
        return self.effective_selling_price_per_pax * self.num_pax

    @property
    def total_profit(self):
        return self.total_revenue - self.total_cost

    @property
    def profit_per_pax(self):
        if self.num_pax == 0:
            return Decimal('0')
        return (self.total_profit / self.num_pax).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    @property
    def margin_percent(self):
        if self.total_revenue == 0:
            return Decimal('0')
        return ((self.total_profit / self.total_revenue) * 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    @property
    def is_feasible(self):
        return self.total_profit >= 0

    def cost_breakdown_by_category(self):
        breakdown = {}
        for item in self.items:
            cat = item.category
            if cat not in breakdown:
                breakdown[cat] = Decimal('0')
            breakdown[cat] += self.item_total_thb(item)
        return breakdown

    def summary(self):
        return {
            'label': self.label,
            'num_pax': self.num_pax,
            'num_tour_leaders': self.num_tour_leaders,
            'markup_percent': str(self.markup_percent),
            'total_cost': str(self.total_cost),
            'cost_per_pax': str(self.cost_per_pax),
            'computed_selling_price_per_pax': str(self.computed_selling_price_per_pax),
            'selling_price_override': str(self.selling_price_per_pax) if self.selling_price_per_pax > 0 else None,
            'effective_selling_price_per_pax': str(self.effective_selling_price_per_pax),
            'total_revenue': str(self.total_revenue),
            'total_profit': str(self.total_profit),
            'profit_per_pax': str(self.profit_per_pax),
            'margin_percent': str(self.margin_percent),
            'is_feasible': self.is_feasible,
            'cost_breakdown': {
                k: str(v) for k, v in self.cost_breakdown_by_category().items()
            },
            'items': [item.to_dict() for item in self.items],
        }


class CostFeasibility:
    """Compares multiple CostScenarios for a tour to evaluate feasibility.

    Models the full spreadsheet: multiple pax-count columns side by side,
    with a comparison summary across all scenarios.
    """

    def __init__(self, tour_name, currency='THB', exchange_rates=None):
        self.tour_name = tour_name
        self.currency = currency
        self.exchange_rates = exchange_rates or {}
        self.scenarios = []

    def add_scenario(self, scenario):
        if not isinstance(scenario, CostScenario):
            raise TypeError("scenario must be a CostScenario instance")
        self.scenarios.append(scenario)
        return scenario

    def remove_scenario(self, index):
        if 0 <= index < len(self.scenarios):
            return self.scenarios.pop(index)
        raise IndexError(f"Scenario index {index} out of range")

    def set_exchange_rate(self, currency_code, rate):
        if rate <= 0:
            raise ValueError("Exchange rate must be positive")
        self.exchange_rates[currency_code] = Decimal(str(rate))

    def convert_to_base(self, amount, from_currency):
        if from_currency == self.currency:
            return Decimal(str(amount))
        if from_currency not in self.exchange_rates:
            raise ValueError(
                f"No exchange rate defined for {from_currency} to {self.currency}"
            )
        return Decimal(str(amount)) * self.exchange_rates[from_currency]

    @property
    def best_scenario(self):
        if not self.scenarios:
            return None
        return max(self.scenarios, key=lambda s: s.margin_percent)

    @property
    def all_feasible(self):
        return all(s.is_feasible for s in self.scenarios)

    def comparison(self):
        return {
            'tour_name': self.tour_name,
            'currency': self.currency,
            'exchange_rates': {
                k: str(v) for k, v in self.exchange_rates.items()
            },
            'all_feasible': self.all_feasible,
            'scenarios': [s.summary() for s in self.scenarios],
        }
