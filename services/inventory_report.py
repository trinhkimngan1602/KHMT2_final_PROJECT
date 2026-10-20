"""Prepare a filtered inventory report without changing stock or stored data."""
from decimal import Decimal


def inventory_report(rows, query='', low_only=False, active_only=False, sort_by='sku'):
    query = query.strip().casefold()
    result = []
    for source in rows:
        row = dict(source)
        row['low_stock'] = bool(row['active']) and row['stock'] < row['min_stock']
        row['shortage'] = max(row['min_stock'] - row['stock'], 0) if row['active'] else 0
        if query and query not in row['sku'].casefold() and query not in row['name'].casefold():
            continue
        if low_only and not row['low_stock']:
            continue
        if active_only and not row['active']:
            continue
        result.append(row)
    if sort_by == 'stock':
        result.sort(key=lambda row: (row['stock'], row['sku']))
    elif sort_by == 'value':
        result.sort(key=lambda row: (-row['stock_value'], row['sku']))
    else:
        result.sort(key=lambda row: row['sku'])
    return dict(rows=result, product_count=len(result),
                low_count=sum(row['low_stock'] for row in result),
                total_value=sum((row['stock_value'] for row in result), Decimal('0.00')))
