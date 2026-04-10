import unittest
from decimal import Decimal
from libs.tours.cost import CostItem, CostScenario, CostFeasibility


class TestCostItem(unittest.TestCase):
    def test_basic_creation(self):
        item = CostItem('Air ticket', 'transportation', 27760)
        self.assertEqual(item.name, 'Air ticket')
        self.assertEqual(item.category, 'transportation')
        self.assertEqual(item.unit_cost, Decimal('27760'))
        self.assertEqual(item.currency, 'THB')

    def test_currency(self):
        item = CostItem('Hotel', 'accommodation', 100, currency='GBP')
        self.assertEqual(item.currency, 'GBP')

    def test_invalid_category(self):
        with self.assertRaises(ValueError):
            CostItem('Bad', 'invalid_cat', 100)

    def test_negative_unit_cost(self):
        with self.assertRaises(ValueError):
            CostItem('Bad', 'other', -100)

    def test_to_dict(self):
        item = CostItem('Visa', 'visa', 2300, pay_to='VFS', currency='THB')
        d = item.to_dict()
        self.assertEqual(d['name'], 'Visa')
        self.assertEqual(d['category'], 'visa')
        self.assertEqual(d['pay_to'], 'VFS')
        self.assertEqual(d['currency'], 'THB')
        self.assertEqual(d['unit_cost'], '2300')
        self.assertNotIn('quantity', d)
        self.assertNotIn('cost_type', d)
        self.assertNotIn('total_cost', d)


class TestCostScenario(unittest.TestCase):
    def _make_scenario(self):
        scenario = CostScenario(num_pax=6, markup_percent=5)
        scenario.add_item(CostItem('Air ticket', 'transportation', 27760))
        scenario.add_item(CostItem('Fuel', 'transportation', 1500))
        return scenario

    def test_total_cost(self):
        scenario = self._make_scenario()
        expected = (Decimal('27760') + Decimal('1500')) * 6
        self.assertEqual(scenario.total_cost, expected)

    def test_item_total_uses_num_pax(self):
        scenario = CostScenario(num_pax=6)
        item = scenario.add_item(CostItem('Air ticket', 'transportation', 27760))
        self.assertEqual(scenario.item_total(item), Decimal('27760') * 6)

    def test_cost_per_pax(self):
        scenario = CostScenario(num_pax=6, markup_percent=5)
        scenario.add_item(CostItem('Item', 'other', 1000))
        self.assertEqual(scenario.cost_per_pax, Decimal('1000.00'))

    def test_computed_selling_price(self):
        scenario = CostScenario(num_pax=2, markup_percent=10)
        scenario.add_item(CostItem('Item', 'other', 1000))
        self.assertEqual(scenario.cost_per_pax, Decimal('1000.00'))
        self.assertEqual(scenario.computed_selling_price_per_pax, Decimal('1100.00'))

    def test_effective_selling_uses_override(self):
        scenario = CostScenario(num_pax=2, markup_percent=10, selling_price_per_pax=5000)
        scenario.add_item(CostItem('Item', 'other', 1000))
        self.assertEqual(scenario.effective_selling_price_per_pax, Decimal('5000'))

    def test_effective_selling_uses_computed_when_zero(self):
        scenario = CostScenario(num_pax=2, markup_percent=10, selling_price_per_pax=0)
        scenario.add_item(CostItem('Item', 'other', 1000))
        self.assertEqual(scenario.effective_selling_price_per_pax, Decimal('1100.00'))

    def test_total_revenue(self):
        scenario = CostScenario(num_pax=6, markup_percent=5)
        scenario.add_item(CostItem('Item', 'other', 10000))
        expected_selling = Decimal('10500.00')
        self.assertEqual(scenario.effective_selling_price_per_pax, expected_selling)
        self.assertEqual(scenario.total_revenue, expected_selling * 6)

    def test_profit_calculation(self):
        scenario = CostScenario(num_pax=2, markup_percent=10, selling_price_per_pax=5000)
        scenario.add_item(CostItem('Cost', 'other', 3000))
        # total cost = 3000 * 2 = 6000; revenue = 5000 * 2 = 10000
        self.assertEqual(scenario.total_profit, Decimal('4000'))
        self.assertEqual(scenario.profit_per_pax, Decimal('2000.00'))

    def test_feasibility(self):
        profitable = CostScenario(num_pax=2, markup_percent=50)
        profitable.add_item(CostItem('Cost', 'other', 100))
        self.assertTrue(profitable.is_feasible)

        losing = CostScenario(num_pax=2, markup_percent=0, selling_price_per_pax=10)
        losing.add_item(CostItem('Cost', 'other', 3000))
        self.assertFalse(losing.is_feasible)

    def test_margin_percent(self):
        scenario = CostScenario(num_pax=2, selling_price_per_pax=10000)
        scenario.add_item(CostItem('Cost', 'other', 5000))
        self.assertEqual(scenario.margin_percent, Decimal('50.00'))

    def test_margin_percent_zero_revenue(self):
        scenario = CostScenario(num_pax=2, markup_percent=0, selling_price_per_pax=0)
        self.assertEqual(scenario.margin_percent, Decimal('0'))

    def test_currency_conversion(self):
        scenario = CostScenario(num_pax=3, markup_percent=0, selling_price_per_pax=100000,
                                exchange_rates={'GBP': Decimal('46')})
        scenario.add_item(CostItem('Hotel', 'accommodation', 100, currency='GBP'))
        scenario.add_item(CostItem('Misc', 'other', 500, currency='THB'))
        # (100 * 46 + 500) * 3 pax
        expected = (Decimal('100') * Decimal('46') + Decimal('500')) * 3
        self.assertEqual(scenario.total_cost, expected)

    def test_currency_conversion_missing_rate(self):
        scenario = CostScenario(num_pax=2, markup_percent=5)
        scenario.add_item(CostItem('Hotel', 'accommodation', 100, currency='EUR'))
        with self.assertRaises(ValueError):
            _ = scenario.total_cost

    def test_cost_breakdown_by_category(self):
        scenario = CostScenario(num_pax=5, markup_percent=5)
        scenario.add_item(CostItem('Hotel A', 'accommodation', 5000))
        scenario.add_item(CostItem('Hotel B', 'accommodation', 3000))
        scenario.add_item(CostItem('Van', 'transportation', 10000))
        breakdown = scenario.cost_breakdown_by_category()
        self.assertEqual(breakdown['accommodation'], Decimal('8000') * 5)
        self.assertEqual(breakdown['transportation'], Decimal('10000') * 5)

    def test_add_remove_item(self):
        scenario = CostScenario(num_pax=5, markup_percent=5)
        scenario.add_item(CostItem('A', 'other', 100))
        scenario.add_item(CostItem('B', 'other', 200))
        self.assertEqual(len(scenario.items), 2)
        removed = scenario.remove_item(0)
        self.assertEqual(removed.name, 'A')
        self.assertEqual(len(scenario.items), 1)

    def test_remove_invalid_index(self):
        scenario = CostScenario(num_pax=5, markup_percent=5)
        with self.assertRaises(IndexError):
            scenario.remove_item(0)

    def test_invalid_num_pax(self):
        with self.assertRaises(ValueError):
            CostScenario(num_pax=0)

    def test_default_markup(self):
        scenario = CostScenario(num_pax=5)
        self.assertEqual(scenario.markup_percent, Decimal('5'))

    def test_summary(self):
        scenario = self._make_scenario()
        s = scenario.summary()
        self.assertEqual(s['num_pax'], 6)
        self.assertIn('total_cost', s)
        self.assertIn('cost_per_pax', s)
        self.assertIn('markup_percent', s)
        self.assertIn('computed_selling_price_per_pax', s)
        self.assertIn('effective_selling_price_per_pax', s)
        self.assertNotIn('personal_cost_total', s)
        self.assertNotIn('shared_cost_total', s)
        self.assertIn('items', s)
        self.assertEqual(len(s['items']), 2)

    def test_summary_selling_price_override(self):
        scenario = CostScenario(num_pax=2, selling_price_per_pax=50000)
        scenario.add_item(CostItem('A', 'other', 100))
        s = scenario.summary()
        self.assertEqual(s['selling_price_override'], '50000')

        scenario2 = CostScenario(num_pax=2)
        scenario2.add_item(CostItem('A', 'other', 100))
        s2 = scenario2.summary()
        self.assertIsNone(s2['selling_price_override'])


class TestCostFeasibility(unittest.TestCase):
    def _make_feasibility(self):
        f = CostFeasibility('Iceland Trip', currency='THB')
        f.set_exchange_rate('USD', 35)
        s1 = CostScenario(num_pax=6, markup_percent=10,
                          exchange_rates={'USD': Decimal('35')})
        s1.add_item(CostItem('Air ticket', 'transportation', 27760))
        s2 = CostScenario(num_pax=8, markup_percent=10,
                          exchange_rates={'USD': Decimal('35')})
        s2.add_item(CostItem('Air ticket', 'transportation', 27760))
        f.add_scenario(s1)
        f.add_scenario(s2)
        return f

    def test_all_feasible(self):
        f = self._make_feasibility()
        self.assertTrue(f.all_feasible)

    def test_best_scenario(self):
        f = self._make_feasibility()
        best = f.best_scenario
        self.assertIsNotNone(best)

    def test_best_scenario_empty(self):
        f = CostFeasibility('Empty')
        self.assertIsNone(f.best_scenario)

    def test_exchange_rate(self):
        f = CostFeasibility('Test', currency='THB')
        f.set_exchange_rate('GBP', 46)
        converted = f.convert_to_base(100, 'GBP')
        self.assertEqual(converted, Decimal('4600'))

    def test_convert_same_currency(self):
        f = CostFeasibility('Test', currency='THB')
        self.assertEqual(f.convert_to_base(500, 'THB'), Decimal('500'))

    def test_convert_unknown_currency(self):
        f = CostFeasibility('Test', currency='THB')
        with self.assertRaises(ValueError):
            f.convert_to_base(100, 'EUR')

    def test_invalid_exchange_rate(self):
        f = CostFeasibility('Test')
        with self.assertRaises(ValueError):
            f.set_exchange_rate('USD', 0)

    def test_comparison(self):
        f = self._make_feasibility()
        c = f.comparison()
        self.assertEqual(c['tour_name'], 'Iceland Trip')
        self.assertEqual(len(c['scenarios']), 2)
        self.assertIn('all_feasible', c)

    def test_add_remove_scenario(self):
        f = CostFeasibility('Test')
        s = CostScenario(num_pax=5)
        f.add_scenario(s)
        self.assertEqual(len(f.scenarios), 1)
        f.remove_scenario(0)
        self.assertEqual(len(f.scenarios), 0)


if __name__ == '__main__':
    unittest.main()
