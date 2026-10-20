"""Fictional, reusable warehouse examples beyond the five original products.

Each movement is (kind, quantity, supplier index, note). Supplier index 0/1
refers to the two existing sample suppliers; 2/3 to EXTRA_SUPPLIERS below.
"""

EXTRA_SUPPLIERS = (
    ('Văn phòng phẩm Xanh', '02838224567'),
    ('Vật tư An Phát', '02838229876'),
)

EXTRA_PRODUCTS = (
    ('SP006', 'Sổ tay A5', 'Cuốn', '45000.00', 6, (('IN', 18, 2, 'Nhập đầu kỳ'), ('OUT', 5, None, 'Cấp phát'))),
    ('SP007', 'Mực máy in', 'Hộp', '320000.00', 3, (('IN', 6, 3, 'Nhập đầu kỳ'), ('OUT', 5, None, 'Cấp phát'))),
    ('SP008', 'Kẹp giấy', 'Hộp', '18000.00', 8, (('IN', 25, 2, 'Nhập đầu kỳ'),)),
    ('SP009', 'Nhãn dán', 'Cuộn', '30000.00', 10, (('IN', 12, 3, 'Nhập đầu kỳ'), ('OUT', 4, None, 'Đóng gói'))),
    ('SP010', 'Dao rọc giấy', 'Cái', '28000.00', 5, (('IN', 8, 0, 'Nhập đầu kỳ'),)),
    ('SP011', 'Bút dạ quang', 'Hộp', '60000.00', 4, (('IN', 5, 2, 'Nhập đầu kỳ'), ('OUT', 5, None, 'Cấp phát hết'))),
    ('SP012', 'Túi đóng gói', 'Gói', '22000.00', 12, (('IN', 24, 3, 'Nhập đầu kỳ'), ('OUT', 11, None, 'Đóng gói'))),
    ('SP013', 'Màng co', 'Cuộn', '95000.00', 6, (('IN', 14, 3, 'Nhập đầu kỳ'), ('OUT', 7, None, 'Đóng gói'))),
    ('SP014', 'Băng mực', 'Hộp', '180000.00', 4, (('IN', 7, 0, 'Nhập đầu kỳ'), ('OUT', 2, None, 'Cấp phát'))),
    ('SP015', 'Khay hồ sơ', 'Cái', '35000.00', 5,
     (('IN', 9, 2, 'Nhập đầu kỳ'), ('ADJUST_OUT', 1, None, 'Hỏng khi kiểm kê'))),
)

# Additional fictional office and packing supplies. Prices are illustrative VND.
# Explicit names keep the sample catalog useful for searching and demonstrations.
CATALOG_50 = (
    ('SP016', 'Bút chì HB', 'Hộp', '24000.00', 8),
    ('SP017', 'Tẩy bút chì', 'Hộp', '20000.00', 6),
    ('SP018', 'Thước kẻ 30 cm', 'Cái', '10000.00', 10),
    ('SP019', 'Kéo văn phòng', 'Cái', '35000.00', 5),
    ('SP020', 'Bấm kim', 'Cái', '65000.00', 4),
    ('SP021', 'Kim bấm số 10', 'Hộp', '8000.00', 15),
    ('SP022', 'Gỡ kim bấm', 'Cái', '18000.00', 5),
    ('SP023', 'Bìa còng A4', 'Cái', '55000.00', 8),
    ('SP024', 'Bìa nút A4', 'Cái', '6000.00', 20),
    ('SP025', 'Bìa lá A4', 'Tập', '40000.00', 6),
    ('SP026', 'Giấy ghi chú', 'Tập', '15000.00', 12),
    ('SP027', 'Giấy A3', 'Ram', '150000.00', 5),
    ('SP028', 'Giấy màu A4', 'Tập', '45000.00', 6),
    ('SP029', 'Phong bì A5', 'Gói', '25000.00', 8),
    ('SP030', 'Bút lông bảng', 'Hộp', '85000.00', 4),
    ('SP031', 'Bút lông dầu', 'Hộp', '95000.00', 4),
    ('SP032', 'Mực dấu', 'Chai', '28000.00', 5),
    ('SP033', 'Khay mực dấu', 'Cái', '38000.00', 4),
    ('SP034', 'Hồ dán', 'Chai', '12000.00', 10),
    ('SP035', 'Băng keo hai mặt', 'Cuộn', '16000.00', 10),
    ('SP036', 'Băng keo giấy', 'Cuộn', '14000.00', 8),
    ('SP037', 'Băng keo dễ vỡ', 'Cuộn', '23000.00', 10),
    ('SP038', 'Màng xốp hơi', 'Cuộn', '180000.00', 3),
    ('SP039', 'Xốp tấm đóng hàng', 'Tấm', '20000.00', 15),
    ('SP040', 'Dây đai nhựa', 'Cuộn', '210000.00', 3),
    ('SP041', 'Dây rút nhựa', 'Gói', '30000.00', 8),
    ('SP042', 'Túi zip', 'Gói', '35000.00', 10),
    ('SP043', 'Túi giấy', 'Gói', '60000.00', 5),
    ('SP044', 'Thùng carton nhỏ', 'Cái', '8000.00', 30),
    ('SP045', 'Thùng carton lớn', 'Cái', '28000.00', 15),
    ('SP046', 'Tem mã vạch', 'Cuộn', '55000.00', 6),
    ('SP047', 'Giấy in nhiệt', 'Cuộn', '18000.00', 10),
    ('SP048', 'Găng tay bảo hộ', 'Đôi', '15000.00', 12),
    ('SP049', 'Khẩu trang bảo hộ', 'Hộp', '45000.00', 8),
    ('SP050', 'Dao cắt băng keo', 'Cái', '55000.00', 5),
)


def sample_movements(index, minimum):
    """Make balanced examples: normal stock, low stock, empty and adjustments."""
    received = minimum * 3 + 5
    supplier = 2 if index < 20 else 3
    rows = [('IN', received, supplier, 'Nhập hàng mẫu bổ sung')]
    if index % 7 == 0:
        rows.append(('OUT', received, None, 'Cấp phát hết hàng mẫu'))
    elif index % 5 == 0:
        rows.append(('OUT', received - max(1, minimum - 2), None, 'Xuất hàng mẫu'))
    else:
        rows.append(('OUT', minimum, None, 'Cấp phát vật tư mẫu'))
        if index % 4 == 0:
            rows.append(('ADJUST_OUT', 1, None, 'Một đơn vị hỏng khi kiểm kê'))
        elif index % 4 == 1:
            rows.append(('ADJUST_IN', 2, None, 'Phát hiện hai đơn vị chưa ghi sổ'))
    return tuple(rows)


EXTRA_PRODUCTS += tuple(
    (*product, sample_movements(index, product[4]))
    for index, product in enumerate(CATALOG_50)
)
