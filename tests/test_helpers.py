import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

scripts = Path(__file__).parents[1] / 'scripts'
sys.path.insert(0, str(scripts))
import memory
spec = importlib.util.spec_from_file_location('grocery_telegram', scripts / 'telegram.py')
telegram = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telegram)

class HelperTests(unittest.TestCase):
    def row(self):
        return dict(id='one', product_id='one', name='Spaghetti', category='spaghetti',
                    store='Gisborne', channel='in-store', price='1.00', quantity='500',
                    unit='g', offer_type='regular', source_url='https://example.invalid/fixture',
                    alcohol=False, observed_at='2026-10-11T08:00:00+13:00')
    def test_duplicate_not_appended(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'prices.jsonl'
            self.assertEqual(memory.append(path, [self.row(), self.row()]), 1)
            self.assertEqual(memory.append(path, [self.row()]), 0)
    def test_invalid_batch_not_partially_written(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'prices.jsonl'
            with self.assertRaises(ValueError):
                memory.append(path, [self.row(), {'id': 'bad'}])
            self.assertFalse(path.exists())
    def test_telegram_splits_long_report(self):
        with patch.dict('os.environ', {'TELEGRAM_CHAT_ID': 'fixture'}):
            with patch.object(telegram, 'request', return_value={}) as sender:
                telegram.send('x' * 8000)
                self.assertEqual(sender.call_count, 3)
                self.assertTrue(all(len(call.args[1]['text']) <= 3500 for call in sender.call_args_list))
    def test_telegram_requires_destination(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                telegram.send('fixture')

if __name__ == '__main__':
    unittest.main()
