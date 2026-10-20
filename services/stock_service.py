from datetime import date, datetime
from models import StockMovement
from .validation import whole_number

MOVEMENT_TYPES = ('IN', 'OUT', 'ADJUST_IN', 'ADJUST_OUT')


def parse_date(value):
    if value is None or value == '':
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError('Ngày phải có dạng YYYY-MM-DD.') from None


class StockService:
    def __init__(self, repository):
        self.repository = repository

    def get_stock(self, product_id):
        return self.repository.get_stock(whole_number(product_id, 'Mã sản phẩm', 1))

    def record_movement(self, product_id, movement_type, quantity, supplier_id=None, note=''):
        if movement_type not in MOVEMENT_TYPES:
            raise ValueError('Loại giao dịch không hợp lệ.')
        product_id = whole_number(product_id, 'Mã sản phẩm', 1)
        quantity = whole_number(quantity, 'Số lượng', 1)
        if supplier_id is not None:
            supplier_id = whole_number(supplier_id, 'Mã nhà cung cấp', 1)
        if movement_type == 'IN' and supplier_id is None:
            raise ValueError('Nhập kho cần chọn nhà cung cấp.')
        if movement_type != 'IN' and supplier_id is not None:
            raise ValueError('Chỉ phiếu nhập kho sử dụng nhà cung cấp.')
        if not isinstance(note, str) or len(note.strip()) > 500:
            raise ValueError('Ghi chú tối đa 500 ký tự.')
        note = note.strip()
        if movement_type.startswith('ADJUST') and not note:
            raise ValueError('Điều chỉnh tồn phải có lý do.')
        return self.repository.record_movement(StockMovement(product_id, movement_type, quantity, supplier_id, note))

    def list_inventory(self):
        return self.repository.list_inventory()

    def list_movements(self, product_id=None, movement_type=None, date_from=None, date_to=None):
        if product_id is not None:
            product_id = whole_number(product_id, 'Mã sản phẩm', 1)
        if movement_type not in (None, *MOVEMENT_TYPES):
            raise ValueError('Loại giao dịch không hợp lệ.')
        date_from, date_to = parse_date(date_from), parse_date(date_to)
        if date_from and date_to and date_from > date_to:
            raise ValueError('Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.')
        return self.repository.list_movements(product_id, movement_type, date_from, date_to)
