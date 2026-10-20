from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    unit: str
    unit_cost: Decimal
    min_stock: int


@dataclass(frozen=True)
class StockMovement:
    product_id: int
    movement_type: str
    quantity: int
    supplier_id: int | None = None
    note: str = ''

    @property
    def signed_quantity(self):
        return self.quantity if self.movement_type in ('IN', 'ADJUST_IN') else -self.quantity
