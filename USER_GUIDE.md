# Hướng dẫn dùng bản đầy đủ

## Mở ứng dụng

Mở PowerShell trong thư mục có main.py. Cài thư viện lần đầu bằng `python -m pip install -r requirements.txt`.

Tập sử dụng bằng `python main.py --demo` hoặc nhấp đúp MO_BAN_MAU.bat. Bản này có dữ liệu mẫu và không lưu sau khi đóng. Để lưu thật: cấu hình config.local.ini, chạy `python setup_db.py` một lần để tạo database và dữ liệu mẫu, rồi `python main.py` hoặc MO_MYSQL.bat. README.md hướng dẫn MySQL chi tiết.

## Mười chức năng ở đâu?

Ứng dụng mở ở **Trang chủ**: ảnh kho, số sản phẩm, nhà cung cấp, hàng dưới mức tối thiểu và tổng giá trị tồn. Số liệu được đọc từ dữ liệu đang dùng; bấm **Làm mới** để cập nhật. Các nút nhanh mở Nhập kho, Xuất kho, Tồn kho và danh sách tồn thấp.

Chọn mục ở **thanh bên trái** hoặc dùng menu **Chức năng** để mở từng màn hình. Các hướng dẫn bên dưới dùng từ “tab” để chỉ mục chức năng tương ứng ở thanh bên. Menu **Ứng dụng** có Làm mới trang hiện tại, Xuất toàn bộ tồn kho CSV và Thoát. Menu **Trợ giúp → Hướng dẫn nhanh** tóm tắt quy trình sử dụng.

Giao diện dùng nền kem, hồng nhạt, tím dịu và nút chính màu cam nổi bật, nút phụ màu xám kem. Trang chủ có thanh cuộn khi cửa sổ thấp. Giữ thư mục `assets/` cạnh `main.py` để ảnh kho luôn hiển thị; không cần cài thêm thư viện đồ họa.

| # | Chức năng | Tab và cách sử dụng |
|---|---|---|
| 1 | Quản lý sản phẩm | Sản phẩm: thêm; chọn dòng để sửa; ngừng dùng/dùng lại khi cần. Ngừng dùng yêu cầu tồn 0. |
| 2 | Quản lý nhà cung cấp | Nhà cung cấp: xem/tìm và thêm tên, điện thoại. Điện thoại có thể trống. |
| 3 | Nhập kho | Nhập kho: chọn sản phẩm, nhà cung cấp, số lượng nguyên dương; lưu. |
| 4 | Xuất kho | Xuất kho: chọn sản phẩm và số lượng. Từ chối xuất quá tồn. |
| 5 | Điều chỉnh tồn | Điều chỉnh: chọn Tăng hoặc Giảm, nhập phần chênh lệch và lý do. |
| 6 | Xem tồn hiện tại | Tồn kho: đọc số lượng, tìm theo mã hoặc tên. |
| 7 | Cảnh báo tồn thấp | Tồn kho: chọn Chỉ hàng tồn thấp, xem số lượng cần bổ sung. |
| 8 | Lịch sử | Lịch sử / CSV: lọc sản phẩm, loại và ngày; bấm Áp dụng bộ lọc. |
| 9 | Giá trị tồn | Tồn kho: xem tồn × đơn giá từng sản phẩm và tổng tiền theo bộ lọc. |
| 10 | Xuất CSV | Lịch sử / CSV: Xuất toàn bộ tồn kho CSV, chọn nơi lưu. |

Các giao dịch đã ghi được giữ làm lịch sử. Khi kiểm kê phát hiện sai lệch, tạo giao dịch điều chỉnh có lý do. Sản phẩm dùng mã SKU cố định; tên và giá có thể sửa. Lịch sử hiển thị tên sản phẩm hiện tại. Giá trị tồn thay đổi khi sửa đơn giá.

Trong bảng tồn, vàng nghĩa là còn hàng nhưng dưới mức tối thiểu; đỏ nghĩa là tồn bằng 0. Mức tối thiểu chỉ nhắc nhập thêm hàng, không chặn xuất nếu kho vẫn đủ số lượng. Các màu cảnh báo áp dụng cho sản phẩm đang dùng.

Màn hình nhập/xuất/điều chỉnh yêu cầu chọn sản phẩm; nhập kho còn cần chọn nhà cung cấp. Nếu sản phẩm đang chọn bị ngừng dùng, ô chọn trở về trống để bạn chọn lại. Khi không đọc được tồn, ứng dụng báo lỗi và giữ nội dung nhập để thử lại.

## Bài tập 10 phút cho người mới

1. Mở bản mẫu mới. Tab Sản phẩm: thêm SKU DEMO10, tên Hàng demo, đơn vị Hộp, đơn giá 50000, tồn tối thiểu 7. Nếu mã đã tồn tại, dùng một mã khác.
2. Tab Nhà cung cấp: thêm NCC demo, điện thoại để trống.
3. Tab Nhập kho: chọn DEMO10 và NCC demo; nhập 10; bấm Lưu giao dịch. Nhìn thông báo thành công và tồn hiện tại 10.
4. Tab Xuất kho: chọn DEMO10; xuất 3. Tồn còn 7.
5. Tab Điều chỉnh: chọn DEMO10, Giảm, số lượng 1, lý do Hỏng khi kiểm kê. Tồn còn 6.
6. Tab Tồn kho: tìm DEMO10. Tồn 6, cần bổ sung 1, giá trị 300.000 VND. Bật Chỉ hàng tồn thấp: dòng này vẫn hiện.
7. Tab Xuất kho: thử xuất 7. Phải thấy lỗi thiếu hàng; tồn vẫn 6. Thông tin nhập giữ lại để sửa.
8. Tab Lịch sử / CSV: chọn DEMO10, bấm Áp dụng bộ lọc. Có 3 giao dịch. Lọc loại Xuất còn 1 giao dịch. Ngày nhập theo YYYY-MM-DD, ví dụ 2026-10-17; có thể để trống.
9. Bấm Xuất toàn bộ tồn kho CSV và chọn nơi lưu. Mở bằng Excel hoặc Notepad, tìm dòng DEMO10: stock bằng 6, stock_value bằng 300000.00. File gồm tất cả sản phẩm, dù trước đó đã lọc bảng tồn/lịch sử.
10. Quay lại Sản phẩm, chọn DEMO10 để sửa tên. Thử Ngừng sử dụng: bị chặn vì còn 6. Chỉ ngừng dùng sau khi xử lý hết tồn.

## Khi gặp lỗi

- Không chọn được sản phẩm: cần có sản phẩm đang dùng ở tab Sản phẩm.
- Nhập kho thiếu nhà cung cấp: thêm ở tab Nhà cung cấp, quay lại tab Nhập kho để danh sách cập nhật.
- Số lượng không hợp lệ: dùng số nguyên dương như 1, 5, 10; không nhập 0, số âm hoặc 1.5.
- Điều chỉnh chưa lưu: ghi lý do và đảm bảo số giảm không vượt tồn.
- Ngày sai: dùng YYYY-MM-DD, ngày đầu không sau ngày cuối.
- CSV không lưu được: đóng file đang mở trong Excel, hoặc chọn thư mục khác có quyền ghi.
- Lỗi MySQL: xem README.md; ảnh lỗi không nên chứa mật khẩu.

## Giải thích code theo cách đơn giản

GUI là màn hình nhận thao tác. Service kiểm tra dữ liệu và quy tắc. Repository đọc/ghi database. Mỗi màn hình gọi service thay vì viết SQL. Ba màn hình nhập/xuất/điều chỉnh kế thừa MovementPage để dùng cùng cách chọn sản phẩm, nhập số lượng, lưu và báo lỗi. Product và StockMovement là các đối tượng dữ liệu. AppContext cung cấp các service cho màn hình.

Đây là mã nguồn ứng dụng. Báo cáo theo mẫu giảng viên, ảnh minh họa và video trình bày của từng thành viên vẫn cần nhóm chuẩn bị.

## Bố cục được chọn

Ảnh kho lớn nằm ngang ở đầu Trang chủ. Cuộn xuống để xem số liệu và nút Nhập kho, Xuất kho. Nút chính dùng màu cam, nút phụ dùng màu xám kem; thanh chức năng vẫn ở bên trái. Ảnh nguồn có kích thước nhỏ nên khi phóng rộng sẽ không sắc nét như ảnh độ phân giải cao.

## Thoát ứng dụng

Bấm X góc trên phải hoặc chọn Ứng dụng → Thoát. Hộp thoại hỏi bạn có chắc muốn thoát không. Chọn Yes để đóng, No để tiếp tục làm việc; mặc định là No. Dữ liệu đã lưu vào MySQL vẫn còn. Nội dung chưa bấm lưu sẽ mất nếu xác nhận thoát; bản mẫu mất toàn bộ thay đổi khi đóng.
