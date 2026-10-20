from decimal import Decimal, InvalidOperation


def whole_number(value, label, minimum=0):
    if isinstance(value, bool):
        raise ValueError(f'{label} phải là số nguyên từ {minimum}.')
    try:
        number = Decimal(str(value))
        if not number.is_finite() or number != number.to_integral_value() or not minimum <= number <= 2147483647:
            raise ValueError
        return int(number)
    except (InvalidOperation, ValueError):
        raise ValueError(f'{label} phải là số nguyên từ {minimum} đến 2147483647.') from None


def required_text(value, label, limit):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise ValueError(f'{label} cần từ 1 đến {limit} ký tự.')
    return value.strip()


def money(value):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or not 0 <= amount <= Decimal('9999999999.99'):
            raise ValueError
        if amount != amount.quantize(Decimal('.01')):
            raise ValueError
        return amount.quantize(Decimal('.01'))
    except (InvalidOperation, ValueError):
        raise ValueError('Đơn giá phải không âm và có tối đa 2 chữ số thập phân.') from None
