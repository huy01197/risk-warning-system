import os
import shutil

# CẤU HÌNH THAM SỐ ĐẦU VÀO ĐỘNG
SAN_GIAO_DICH = 'HNX'       # 'HSX' hoặc 'HNX'
SO_NAM_LICH_SU = 5          # 5 năm chuỗi thời gian

def khoi_tao_thu_muc_xuat(exchange, nam_phan_tich):
    """Khởi tạo và tự động làm sạch thư mục lưu trữ báo cáo."""
    thu_muc = f"BaoCao_RuiRo_{exchange}_{nam_phan_tich}"
    if os.path.exists(thu_muc):
        shutil.rmtree(thu_muc)
    os.makedirs(thu_muc, exist_ok=True)
    return thu_muc