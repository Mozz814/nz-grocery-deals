"""Append validated observations to a private JSONL history without duplicates."""
import json
import sys
from pathlib import Path
from datetime import datetime
from compare import unit_price

def append(path, rows):
    path = Path(path)
    prior = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()] if path.exists() else []
    known = {row['id'] for row in prior}
    additions = []
    for row in rows:
        for key in ('id', 'observed_at', 'product_id', 'name', 'category', 'store', 'channel', 'price', 'quantity', 'unit', 'offer_type', 'source_url', 'alcohol'):
            if key not in row:
                raise ValueError('Missing field: ' + key)
        if datetime.fromisoformat(row['observed_at']).utcoffset() is None:
            raise ValueError('Timestamp must include timezone')
        unit_price(dict(row, alcohol=False))
        if row['id'] not in known:
            additions.append(row)
            known.add(row['id'])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        for row in additions:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    return len(additions)

if __name__ == '__main__':
    with open(sys.argv[2], encoding='utf-8') as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    print('Added', append(sys.argv[1], rows), 'observations')
