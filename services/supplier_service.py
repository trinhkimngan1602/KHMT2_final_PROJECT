"""Supplier input validation shared by the UI and both repositories."""
from .validation import required_text


class SupplierService:
    def __init__(self, repository):
        self.repository = repository

    def list_suppliers(self):
        return self.repository.list_suppliers()

    def create_supplier(self, name: str, phone: str) -> int:
        name = required_text(name, 'Tên nhà cung cấp', 120)
        if not isinstance(phone, str) or len(phone.strip()) > 30:
            raise ValueError('Số điện thoại tối đa 30 ký tự; có thể để trống.')
        return self.repository.insert_supplier(name, phone.strip())
