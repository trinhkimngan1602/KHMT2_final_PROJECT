import argparse
import sys
from services.context import build_context
from ui.app import WarehouseApp
from database import StorageError


def main():
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description='Warehouse management — Python, Tkinter, MySQL')
    parser.add_argument('--demo',action='store_true',help='Use in-memory sample data, explicitly without MySQL')
    args=parser.parse_args()
    try:
        context=build_context(demo=args.demo)
    except StorageError as exc:
        print(str(exc))
        print('Cấu hình MySQL hoặc chạy python main.py --demo.')
        return 1
    app=WarehouseApp(context)
    app.mainloop()
    return 0


if __name__=='__main__':
    raise SystemExit(main())
