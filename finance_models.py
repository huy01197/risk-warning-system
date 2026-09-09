import numpy as np
import pandas as pd

def tinh_altman_z_score(df):
    """
    Tính toán Altman Z-Score 5 chỉ số thành phần chuẩn cho DN niêm yết:
    X1 = Vốn lưu động / Tổng tài sản
    X2 = Lợi nhuận giữ lại (LN chưa phân phối) / Tổng tài sản
    X3 = EBIT / Tổng tài sản
    X4 = Vốn chủ sở hữu / Nợ phải trả (Phiên bản cải tiến phù hợp dữ liệu BCTC)
    X5 = Doanh thu thuần / Tổng tài sản
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
    """
    df_out = df.copy()

    von_luu_dong = df_out['Tai_San_Ngan_Han'] - df_out['No_Ngan_Han']
    ebit = df_out['Loi_Nhuan_Truoc_Thue'] + df_out['Chi_Phi_Lai_Vay']

    df_out['X1_VonLuuDong'] = (von_luu_dong / df_out['Tong_Tai_San']).round(4)
    df_out['X2_LNChuaPhanPhoi'] = (df_out['LN_Chua_Phan_Phoi'] / df_out['Tong_Tai_San']).round(4)
    df_out['X3_EBIT'] = (ebit / df_out['Tong_Tai_San']).round(4)
    df_out['X4_VCSH_No'] = np.where(df_out['No_Phai_Tra'] > 0, df_out['Von_Chu_So_Huu'] / df_out['No_Phai_Tra'], 1.0).round(4)
    df_out['X5_DoanhThu'] = (df_out['Doanh_Thu'] / df_out['Tong_Tai_San']).round(4)

    df_out['Z_Score'] = (
        1.2 * df_out['X1_VonLuuDong'] +
        1.4 * df_out['X2_LNChuaPhanPhoi'] +
        3.3 * df_out['X3_EBIT'] +
        0.6 * df_out['X4_VCSH_No'] +
        0.999 * df_out['X5_DoanhThu']
    ).round(2)

    return df_out

def tinh_beneish_m_score(df):
    """
    Tính toán Beneish M-Score chuỗi thời gian (Năm t so với Năm t-1):
    DSRI: Chỉ số số ngày thu tiền
    GMI:  Chỉ số biên lợi nhuận gộp
    AQI:  Chỉ số chất lượng tài sản
    SGI:  Chỉ số tăng trưởng doanh thu
    DEPI: Chỉ số tỷ lệ khấu hao
    M = -6.065 + 0.823*DSRI + 0.906*GMI + 0.593*AQI + 0.717*SGI + 0.107*DEPI
    """
    df_out = df.sort_values(by=['Ma_CP', 'Nam']).copy()

    # Kiểm tra tính liên tục của chuỗi thời gian (phải là 2 năm liên tiếp)
    df_out['Nam_prev'] = df_out.groupby('Ma_CP')['Nam'].shift(1)
    la_nam_lien_ke = (df_out['Nam'] - df_out['Nam_prev']) == 1

    # 1. DSRI (Days Sales in Receivables Index)
    df_out['DSR'] = np.where(df_out['Doanh_Thu'] > 0, df_out['Phai_Thu_Ngan_Han'] / df_out['Doanh_Thu'], np.nan)
    df_out['DSR_prev'] = df_out.groupby('Ma_CP')['DSR'].shift(1)
    df_out['DSRI'] = np.where(la_nam_lien_ke & (df_out['DSR_prev'] > 0), df_out['DSR'] / df_out['DSR_prev'], 1.0)

    # 2. GMI (Gross Margin Index = GPM_(t-1) / GPM_t)
    df_out['GPM'] = np.where(df_out['Doanh_Thu'] > 0, df_out['Loi_Nhuan_Gop'] / df_out['Doanh_Thu'], np.nan)
    df_out['GPM_prev'] = df_out.groupby('Ma_CP')['GPM'].shift(1)
    df_out['GMI'] = np.where(la_nam_lien_ke & (df_out['GPM'] > 0), df_out['GPM_prev'] / df_out['GPM'], 1.0)

    # 3. AQI (Asset Quality Index)
    ts_khong_sx = 1.0 - (df_out['Tai_San_Ngan_Han'] + df_out['Tai_San_Co_Dinh']) / df_out['Tong_Tai_San']
    ts_khong_sx = np.clip(ts_khong_sx, 0.0, 1.0)
    df_out['AQ'] = ts_khong_sx
    df_out['AQ_prev'] = df_out.groupby('Ma_CP')['AQ'].shift(1)
    df_out['AQI'] = np.where(la_nam_lien_ke & (df_out['AQ_prev'] > 0), df_out['AQ'] / df_out['AQ_prev'], 1.0)

    # 4. SGI (Sales Growth Index)
    df_out['Doanh_Thu_prev'] = df_out.groupby('Ma_CP')['Doanh_Thu'].shift(1)
    df_out['SGI'] = np.where(la_nam_lien_ke & (df_out['Doanh_Thu_prev'] > 0), df_out['Doanh_Thu'] / df_out['Doanh_Thu_prev'], 1.0)

    # 5. DEPI (Depreciation Index)
    tong_tscd = df_out['Tai_San_Co_Dinh'] + df_out['Chi_Phi_Khau_Hao']
    df_out['Depr_Rate'] = np.where(tong_tscd > 0, df_out['Chi_Phi_Khau_Hao'] / tong_tscd, 0.05)
    df_out['Depr_Rate_prev'] = df_out.groupby('Ma_CP')['Depr_Rate'].shift(1)
    df_out['DEPI'] = np.where(la_nam_lien_ke & (df_out['Depr_Rate'] > 0), df_out['Depr_Rate_prev'] / df_out['Depr_Rate'], 1.0)

    for col in ['DSRI', 'GMI', 'AQI', 'SGI', 'DEPI']:
        df_out[col] = np.where(la_nam_lien_ke, df_out[col], np.nan)
        df_out[col] = df_out[col].replace([np.inf, -np.inf], np.nan).fillna(1.0)
        df_out[col] = df_out[col].round(4)

    df_out['M_Score'] = np.where(
        la_nam_lien_ke,
        -6.065 + 0.823 * df_out['DSRI'] + 0.906 * df_out['GMI'] + 0.593 * df_out['AQI'] + 0.717 * df_out['SGI'] + 0.107 * df_out['DEPI'],
        np.nan
    )
    df_out['M_Score'] = df_out['M_Score'].round(2)

    # Dọn dẹp các cột phụ trợ
    cols_to_drop = ['Nam_prev', 'DSR', 'DSR_prev', 'GPM', 'GPM_prev', 'AQ', 'AQ_prev', 'Doanh_Thu_prev', 'Depr_Rate', 'Depr_Rate_prev']
    df_out.drop(columns=[c for c in cols_to_drop if c in df_out.columns], inplace=True)

    return df_out

def phan_loai_canh_bao(df):
    """
    Gán nhãn cảnh báo rủi ro dựa trên ngưỡng chuẩn lý thuyết:
    1. Cảnh báo Z-Score (3 mức theo đề bài):
       - Z > 2.99: 'Vùng an toàn'
       - 1.81 <= Z <= 2.99: 'Vùng xám'
       - Z < 1.81: 'Vùng nguy hiểm'
    2. Cảnh báo M-Score (2 mức theo đề bài):
       - M > -1.78: 'Có khả năng cao thao túng BCTC'
       - M <= -1.78: 'Ít có khả năng thao túng'
    3. Trạng thái rủi ro tổng hợp 4 góc phần tư (theo biểu đồ mẫu):
       - 'An toàn': Z >= 1.81, M < -1.78
       - 'Nghi vấn gian lận': Z >= 1.81, M >= -1.78
       - 'Nguy cơ phá sản': Z < 1.81, M < -1.78
       - 'Khủng hoảng kép': Z < 1.81, M >= -1.78
    """
    def gan_nhan_z(z):
        if pd.isna(z):
            return 'Chưa đủ dữ liệu'
        if z > 2.99:
            return 'Vùng an toàn'
        elif z >= 1.81:
            return 'Vùng xám'
        else:
            return 'Vùng nguy hiểm'

    def gan_nhan_m(m):
        if pd.isna(m):
            return 'Chưa đủ dữ liệu'
        if m > -1.78:
            return 'Có khả năng cao thao túng BCTC'
        else:
            return 'Ít có khả năng thao túng'

    def gan_nhan_tong_hop(row):
        z, m = row['Z_Score'], row['M_Score']
        if pd.isna(z) or pd.isna(m):
            return 'Chưa đủ dữ liệu'
        if z >= 1.81 and m < -1.78:
            return 'An toàn'
        elif z >= 1.81 and m >= -1.78:
            return 'Nghi vấn gian lận'
        elif z < 1.81 and m < -1.78:
            return 'Nguy cơ phá sản'
        else:  # z < 1.81 và m >= -1.78
            return 'Khủng hoảng kép'

    df_out = df.copy()
    df_out['Canh_Bao_Z'] = df_out['Z_Score'].apply(gan_nhan_z)
    df_out['Canh_Bao_M'] = df_out['M_Score'].apply(gan_nhan_m)
    df_out['Trang_Thai_Rui_Ro'] = df_out.apply(gan_nhan_tong_hop, axis=1)
    df_out['Nhan_Canh_Bao'] = df_out['Trang_Thai_Rui_Ro']  # Alias tương thích ngược

    return df_out

def tim_top_doanh_nghiep_suy_thoai(df, top_n=2):
    """
    Tự động quét và chọn 1-2 doanh nghiệp có biến động tiêu cực nhất qua các năm:
    - Thể hiện rõ sự suy giảm của Z-Score (delta_z < 0) VÀ sự gia tăng của M-Score (delta_m > 0).
    - Ưu tiên doanh nghiệp bắt đầu ở vùng an toàn/vùng xám (Z >= 1.81) rồi suy thoái xuống vùng nguy hiểm (Z < 1.81),
      đồng thời M-Score tăng vượt ngưỡng thao túng (M >= -1.78) để rơi vào trạng thái 'Khủng hoảng kép'.
    - Lọc bỏ các giá trị ngoại lai dị thường (outliers do mẫu số gần 0) để bảo toàn tỷ lệ trực quan của đồ thị.
    """
    df_valid = df.dropna(subset=['Z_Score', 'M_Score']).copy()
    danh_sach = []

    for tk in df_valid['Ma_CP'].unique():
        df_tk = df_valid[df_valid['Ma_CP'] == tk].sort_values('Nam')
        if len(df_tk) >= 3:
            z_dau, z_cuoi = df_tk['Z_Score'].iloc[0], df_tk['Z_Score'].iloc[-1]
            m_dau, m_cuoi = df_tk['M_Score'].iloc[0], df_tk['M_Score'].iloc[-1]

            # Loại bỏ ngoại lai dị thường làm méo tỷ lệ đồ thị
            if (df_tk['M_Score'].max() > 12 or df_tk['M_Score'].min() < -8 or
                df_tk['Z_Score'].max() > 25 or df_tk['Z_Score'].min() < -10):
                continue

            delta_z = z_cuoi - z_dau  # Âm = Z suy giảm
            delta_m = m_cuoi - m_dau  # Dương = M gia tăng

            # Chỉ chọn nếu đồng thời Z suy giảm VÀ M gia tăng
            if delta_z < 0 and delta_m > 0:
                priority = 0
                if z_cuoi < 1.81:
                    priority += 10
                if m_cuoi >= -1.78:
                    priority += 10
                if z_dau >= 1.81 and z_cuoi < 1.81:
                    priority += 10

                norm_z = -delta_z / max(abs(z_dau), 1.0)
                norm_m = delta_m / max(abs(m_dau), 1.0)
                score = priority + norm_z * 5.0 + norm_m * 5.0

                danh_sach.append({
                    'Ma_CP': tk,
                    'Delta_Z': delta_z,
                    'Delta_M': delta_m,
                    'Diem': score
                })

    # Nếu không tìm thấy mã thỏa mãn cả 2 điều kiện, mở rộng tìm kiếm fallback
    if not danh_sach:
        for tk in df_valid['Ma_CP'].unique():
            df_tk = df_valid[df_valid['Ma_CP'] == tk].sort_values('Nam')
            if len(df_tk) >= 3:
                z_dau, z_cuoi = df_tk['Z_Score'].iloc[0], df_tk['Z_Score'].iloc[-1]
                m_dau, m_cuoi = df_tk['M_Score'].iloc[0], df_tk['M_Score'].iloc[-1]
                delta_z = z_cuoi - z_dau
                delta_m = m_cuoi - m_dau
                danh_sach.append({
                    'Ma_CP': tk,
                    'Delta_Z': delta_z,
                    'Delta_M': delta_m,
                    'Diem': (-delta_z) + delta_m
                })

    if not danh_sach:
        return []

    df_rank = pd.DataFrame(danh_sach).sort_values(by='Diem', ascending=False)
    return df_rank['Ma_CP'].head(top_n).tolist()