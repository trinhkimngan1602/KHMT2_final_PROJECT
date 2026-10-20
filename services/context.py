from dataclasses import dataclass
from .product_service import ProductService
from .stock_service import StockService
from .supplier_service import SupplierService


@dataclass
class AppContext:
    product_service: ProductService
    supplier_service: SupplierService
    stock_service: StockService
    demo: bool = False


def build_context(demo=False, settings=None):
    if demo:
        from repositories.memory_repository import MemoryRepository
        repository = MemoryRepository()
    else:
        from database import Database
        from repositories.mysql_repository import MySQLRepository
        repository = MySQLRepository(Database(settings))
    return AppContext(ProductService(repository), SupplierService(repository), StockService(repository), demo)
