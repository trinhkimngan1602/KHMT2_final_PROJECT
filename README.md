# Ứng dụng quản lý kho

Dự án Khoa học Máy tính 2 dùng Python OOP, Tkinter/ttk và MySQL.

## Chức năng

Quản lý sản phẩm, nhà cung cấp, nhập kho, xuất kho, điều chỉnh tồn, tra cứu tồn, cảnh báo tồn thấp, lịch sử giao dịch, giá trị hàng tồn và xuất CSV. Có xác nhận trước khi thoát ứng dụng.

## Chạy bản mẫu

Cần Python 3.10 trở lên có Tkinter. Mở terminal tại thư mục chứa main.py:

```powershell
python -m pip install -r requirements.txt
python main.py --demo
```

Có thể mở MO_BAN_MAU.bat sau khi đã cài thư viện. Bộ mẫu gồm 50 sản phẩm, 4 nhà cung cấp và 106 giao dịch hư cấu. Thay đổi trong chế độ mẫu mất khi đóng app.

## Chạy bằng MySQL

1. Cài và khởi động MySQL 8.0.16 trở lên.
2. Sao chép config.example.ini thành config.local.ini và điền thông tin kết nối của máy bạn.
3. Chạy các lệnh sau tại thư mục dự án:

```powershell
python setup_db.py
python main.py
```

Có thể dùng MO_MYSQL.bat để mở app. setup_db.py tạo schema và chỉ nạp dữ liệu mẫu khi cả ba bảng đều rỗng. Nếu database đã có dữ liệu, dùng `python expand_sample.py` để thêm các SKU mẫu còn thiếu; chạy lại không thêm trùng. Không chạy seed.sql trực tiếp lên các bảng đã có dữ liệu.

Không đưa config.local.ini lên GitHub vì file chứa cấu hình riêng và mật khẩu. Mỗi máy tự tạo file này. GitHub lưu mã nguồn, không tự đồng bộ dữ liệu MySQL giữa các máy.

## Cấu trúc

- main.py: điểm khởi động ứng dụng.
- models: đối tượng sản phẩm và giao dịch.
- ui: giao diện Tkinter.
- services: kiểm tra dữ liệu và quy tắc nghiệp vụ.
- repositories: đọc ghi MySQL hoặc bộ nhớ cho bản mẫu.
- database.py: cấu hình và kết nối database.
- schema.sql: cấu trúc ba bảng products, suppliers, stock_movements.
- seed.sql và sample_data.py: bộ dữ liệu mẫu.
- assets: ảnh cần cho giao diện và thông tin nguồn ảnh.
- tests: kiểm tra nghiệp vụ, giao diện, CSV và MySQL.

Luồng xử lý: GUI gọi service, service gọi repository, repository làm việc với MySQL. Số tồn tính từ giao dịch nhập và tăng, trừ xuất và giảm. Giá trị tồn dùng đơn giá hiện tại, chưa phải FIFO hoặc giá vốn bình quân.

## Kiểm tra

```powershell
python -m unittest discover -s tests -v
```

Kiểm tra MySQL mặc định bị bỏ qua. Để chạy cả MySQL, cần cấu hình kết nối và quyền tạo database thử:

```powershell
$env:WAREHOUSE_TEST_MYSQL = '1'
python -m unittest discover -s tests -v
```

Các kiểm tra MySQL tạo rồi xóa database thử có tên ngẫu nhiên. Kiểm tra giao diện cần môi trường có màn hình và Tkinter.

## Hướng dẫn sử dụng

Xem USER_GUIDE.md. Giữ nguyên thư mục assets khi sao chép dự án. Báo cáo Word và video được bàn giao riêng.
