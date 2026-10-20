from models import Product
from .validation import required_text, whole_number, money


class ProductService:
    def __init__(self, repository):
        self.repository = repository

    def list_products(self):
        return self.repository.list_products()

    def create_product(self, sku, name, unit, unit_cost, min_stock=0):
        product = Product(required_text(sku, 'SKU', 40).upper(),
                          required_text(name, 'Tên sản phẩm', 120),
                          required_text(unit, 'Đơn vị', 30), money(unit_cost),
                          whole_number(min_stock, 'Mức tồn tối thiểu'))
        return self.repository.create_product(product)

    def update_product(self, product_id, name, unit, unit_cost, min_stock=0):
        product_id = whole_number(product_id, 'ID sản phẩm', 1)
        name = required_text(name, 'Tên sản phẩm', 120)
        unit = required_text(unit, 'Đơn vị', 30)
        unit_cost = money(unit_cost)
        min_stock = whole_number(min_stock, 'Mức tồn tối thiểu')
        self.repository.update_product(product_id, name, unit, unit_cost, min_stock)

    def set_product_active(self, product_id, active):
        product_id = whole_number(product_id, 'ID sản phẩm', 1)
        if not isinstance(active, bool):
            raise ValueError('Trạng thái sản phẩm không hợp lệ.')
        self.repository.set_product_active(product_id, active)
