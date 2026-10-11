import importlib.util
from pathlib import Path
import unittest
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
        self.assertEqual(summary['change_nzd'], '-0.40')
        self.assertEqual(summary['change_percent'], '-20.0')

if __name__ == '__main__':
    unittest.main()
