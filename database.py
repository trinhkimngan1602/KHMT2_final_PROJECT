"""Read local connection settings and open short-lived MySQL transactions."""
import configparser
from contextlib import contextmanager
from pathlib import Path

import mysql.connector

ROOT = Path(__file__).resolve().parent


class StorageError(RuntimeError):
    pass


def load_settings(path=None):
    path = Path(path or ROOT / 'config.local.ini')
    parser = configparser.ConfigParser(interpolation=None)
    if not path.exists():
        raise StorageError('Thiếu config.local.ini. Sao chép config.example.ini rồi điền thông tin MySQL.')
    try:
        with path.open(encoding='utf-8-sig') as stream:
            parser.read_file(stream)
        section = parser['mysql']
        settings = dict(host=section.get('host', '127.0.0.1'), port=section.getint('port', 3306),
                    user=section['user'], password=section.get('password', ''),
                    database=section.get('database', 'warehouse_mgmt'),
                    charset='utf8mb4', connection_timeout=5)
        if not 1 <= settings['port'] <= 65535 or any(
                not settings[key].strip() for key in ('host', 'user', 'database')):
            raise ValueError
        return settings
    except (KeyError, ValueError, OSError, configparser.Error):
        raise StorageError('Không đọc được cấu hình MySQL. Kiểm tra file UTF-8, mục [mysql], '
                           'host, user, database và port từ 1 đến 65535.') from None


class Database:
    def __init__(self, settings=None):
        self.settings = settings or load_settings()

    @contextmanager
    def transaction(self):
        connection = None
        try:
            connection = mysql.connector.connect(**self.settings)
            connection.start_transaction(isolation_level='READ COMMITTED')
            yield connection
            connection.commit()
        except mysql.connector.Error as exc:
            if connection is not None:
                connection.rollback()
            raise StorageError(f'Lỗi MySQL {exc.errno}. Kiểm tra cấu hình, dịch vụ và schema.sql.') from exc
        except Exception:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if connection is not None:
                connection.close()
