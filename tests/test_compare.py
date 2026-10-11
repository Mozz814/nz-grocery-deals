import importlib.util
from pathlib import Path
import unittest
from decimal import Decimal
from datetime import datetime, timezone
spec = importlib.util.spec_from_file_location('compare', Path(__file__).parents[1] / 'scripts' / 'compare.py')
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)

class CompareTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(product_id='pasta500', name='Pasta 500g', category='spaghetti',
                   store='Gisborne', channel='online', price='1.60', quantity='500', unit='g',
                   offer_type='sale', alcohol=False, observed_at='2026-10-11T08:00:00+13:00')
        row.update(changes)
        return row
    def test_regular_larger_pack_beats_sale(self):
        rows = [self.row(), self.row(product_id='pasta1000', name='Pasta 1kg', price='2.80', quantity='1000', offer_type='regular')]
        results = compare.better_regulars(rows, datetime.fromisoformat('2026-10-11T09:00:00+13:00'))
        self.assertEqual(results[0]['conclusion'], 'regular cheaper')
    def test_alcohol_excluded(self):
        self.assertIsNone(compare.unit_price(self.row(alcohol=True)))
    def test_reference_requires_opt_in_and_is_labelled(self):
        rows = [self.row(store='Napier', price_scope='reference'), self.row(product_id='other', price='1.00', offer_type='regular')]
        now = datetime.fromisoformat('2026-10-11T09:00:00+13:00')
        self.assertEqual(compare.better_regulars(rows, now), [])
        self.assertTrue(compare.better_regulars(rows, now, include_reference=True)[0]['approximate'])
    def test_history_keeps_scopes_separate(self):
        prior = self.row(price_scope='reference', observed_at='2026-10-10T08:00:00+13:00')
        self.assertEqual(compare.history_summary([prior], self.row())['coverage_observations'], 0)
    def test_single_and_multibuy_both_compared(self):
        rows = [self.row(price='3.29', offer_type='regular'),
                self.row(price='5.00', quantity='1000', minimum_purchase=2, offer_type='multibuy'),
                self.row(product_id='essentials', name='Essentials', price='1.49', offer_type='regular')]
        results = compare.better_regulars(rows, datetime.fromisoformat('2026-10-11T09:00:00+13:00'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['regular'], 'Essentials')
    def test_expired_or_wrong_units_excluded(self):
        rows = [self.row(expires_at='2026-10-11T08:30:00+13:00'), self.row(product_id='other', offer_type='regular', price='0.10', unit='ml')]
        self.assertEqual(compare.better_regulars(rows, datetime.fromisoformat('2026-10-11T09:00:00+13:00')), [])
    def test_stale_price_not_current(self):
        self.assertEqual(compare.better_regulars([self.row()], datetime(2026, 10, 15, tzinfo=timezone.utc)), [])
    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            compare.unit_price(self.row(quantity='0'))
    def test_exclusive_brand(self):
        rows = [self.row(exclusive_brand='So Good', brand='So Good'), self.row(product_id='other', brand='Other', offer_type='regular', price='0.10')]
        self.assertEqual(compare.better_regulars(rows, datetime.fromisoformat('2026-10-11T09:00:00+13:00')), [])
    def test_history_excludes_alcohol(self):
        self.assertIsNone(compare.history_summary([], self.row(alcohol=True)))
    def test_historical_price_change(self):
        prior = self.row(price='2.00', observed_at='2026-10-10T08:00:00+13:00')
        summary = compare.history_summary([prior], self.row())
        self.assertEqual(Decimal(summary['change_nzd']), Decimal('-0.40'))
        self.assertEqual(Decimal(summary['change_percent']), Decimal('-20.0'))
    def test_history_normalizes_multibuy_quantity(self):
        prior = self.row(price='3.00', quantity='1000', offer_type='multibuy', observed_at='2026-10-10T08:00:00+13:00')
        summary = compare.history_summary([prior], self.row(price='1.60', quantity='500'))
        self.assertEqual(summary['previous_price'], '1.500')
        self.assertEqual(summary['change_nzd'], '0.100')
        self.assertEqual(summary['previous_total_paid'], '3.00')
    def test_history_rejects_incompatible_units(self):
        prior = self.row(unit='ml', observed_at='2026-10-10T08:00:00+13:00')
        with self.assertRaises(ValueError):
            compare.history_summary([prior], self.row())

if __name__ == '__main__':
    unittest.main()
