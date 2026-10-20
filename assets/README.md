# Ảnh trang chủ

`warehouse.png` là ảnh kho do người dùng gửi trong cuộc trò chuyện ngày 17/10/2026.
File được sao chép nguyên bản; giao diện Tkinter hiển thị ảnh trong khung trang chủ.
Giữ thư mục assets cạnh main.py khi sao chép hoặc giải nén ứng dụng.

## Bản ảnh rõ hơn ngày 19/10/2026

`warehouse_hd.png` là ảnh minh họa được tạo lại từ ảnh gốc bằng công cụ imagegen tích hợp.
Đây là ảnh có AI hỗ trợ dựng lại chi tiết, không phải bản phục hồi chính xác từng chi tiết của ảnh gốc.
App chỉ đọc PNG bằng `tkinter.PhotoImage`, không kết nối dịch vụ tạo ảnh khi chạy.
Ảnh chỉ thu nhỏ hoặc cắt khung, không phóng lớn ảnh nhỏ.

Prompt đã dùng:
Edit this low-resolution warehouse reference into a high-resolution wide warehouse photograph for a desktop inventory application banner. Preserve the warehouse subject, elevated centered perspective, racks, pallets and warm light, but reconstruct crisp believable straight architectural lines and realistic boxes. Natural documentary photo, subdued warmth, no exaggerated sunbeams, no illustration or glossy promotional aesthetic. Wide landscape composition at least 1536 pixels wide, preferably 2048 wide; keep the warehouse readable in a wide center crop. No lettering, logos, watermark or interface. This is an illustrative improved version, not forensic recovery of original details.
