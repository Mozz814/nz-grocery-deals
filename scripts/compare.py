"""Compare verified compatible observations; never compare alcohol."""
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal

def unit_price(row):
    if row.get('alcohol'):
        return None
    price, quantity = Decimal(row['price']), Decimal(row['quantity'])
    if price < 0 or quantity <= 0:
        raise ValueError('Invalid price or quantity')
    factors = {'g': 100, 'ml': 100, 'egg': 1, 'wash': 1, 'sheet': 100, 'item': 1}
    return price / quantity * factors[row['unit']]

def better_regulars(rows, now=None):
    now = now or datetime.now(timezone.utc)
    current = {}
    for row in rows:
        stamp = datetime.fromisoformat(row['observed_at'])
        if stamp.utcoffset() is None:
            raise ValueError('Timestamp must have timezone')
        if stamp > now:
            continue
        key = (row['product_id'], row['store'], row['channel'])
        if key not in current or stamp > datetime.fromisoformat(current[key]['observed_at']):
            current[key] = row
    eligible = []
    for row in current.values():
        if row.get('alcohol') or row.get('in_stock') is False:
            continue
        if (now - datetime.fromisoformat(row['observed_at'])).total_seconds() > 86400:
            continue
        if row.get('expires_at') and datetime.fromisoformat(row['expires_at']) <= now:
            continue
        unit_price(row)
        eligible.append(row)
    result = []
    for offer in eligible:
        if offer['offer_type'] == 'regular':
            continue
        for regular in eligible:
            if regular['offer_type'] != 'regular':
                continue
            keys = ('category', 'unit', 'channel')
            if any(regular[k] != offer[k] for k in keys):
                continue
            if offer.get('exclusive_brand') and regular.get('brand') != offer['exclusive_brand']:
                continue
            if unit_price(regular) <= unit_price(offer):
                result.append({'offer': offer['name'], 'offer_store': offer['store'],
                               'regular': regular['name'], 'regular_store': regular['store'],
                               'offer_unit_price': str(unit_price(offer)),
                               'regular_unit_price': str(unit_price(regular)),
                               'conclusion': 'equal' if unit_price(regular) == unit_price(offer) else 'regular cheaper'})
    return result

def history_summary(rows, fresh):
    if fresh.get('alcohol'):
        return None
    instant = datetime.fromisoformat(fresh['observed_at'])
    keys = ('product_id', 'store', 'channel')
    prior = [r for r in rows if not r.get('alcohol') and all(r[k] == fresh[k] for k in keys)
             and datetime.fromisoformat(r['observed_at']) < instant]
    prior.sort(key=lambda r: datetime.fromisoformat(r['observed_at']))
    if not prior:
        return {'previous_price': None, 'coverage_observations': 0}
    previous = Decimal(prior[-1]['price'])
    delta = Decimal(fresh['price']) - previous
    sales = [r for r in prior if r['offer_type'] != 'regular']
    summary = {'previous_price': str(previous), 'change_nzd': str(delta),
               'change_percent': str(delta / previous * 100) if previous else None,
               'previous_sale': sales[-1]['price'] if sales else None,
               'coverage_observations': len(prior)}
    for days in (30, 90):
        window = [Decimal(r['price']) for r in prior if (instant - datetime.fromisoformat(r['observed_at'])).total_seconds() <= days * 86400]
        summary[f'observed_low_{days}d'] = str(min(window)) if window else None
    return summary

if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as stream:
        print(json.dumps(better_regulars([json.loads(line) for line in stream if line.strip()]), indent=2))
