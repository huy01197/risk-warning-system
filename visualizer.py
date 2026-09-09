import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def ve_ma_tran_toan_san(df, nam, exchange, thu_muc_luu):
    """
    Vẽ Biểu đồ Phân tán Bốn góc phần tư (4-Quadrant Scatter Plot) chuẩn theo tài liệu:
    - Trục X: Beneish M-Score (Ngưỡng phân tách tại -1.78)
    - Trục Y: Altman Z-Score (Ngưỡng phân tách tại 1.81 và 2.99)
    - 4 góc phần tư rủi ro tổng hợp:
      + An toàn (Z >= 1.81, M < -1.78)
      + Nghi vấn gian lận (Z >= 1.81, M >= -1.78)
      + Nguy cơ phá sản (Z < 1.81, M < -1.78)
      + Khủng hoảng kép (Z < 1.81, M >= -1.78)
    """
    df_nam = df[(df['Nam'] == nam) & (df['Trang_Thai_Rui_Ro'].isin([
        'An toàn', 'Nguy cơ phá sản', 'Nghi vấn gian lận', 'Khủng hoảng kép'
    ]))].copy()

    if df_nam.empty:
        print(f"  > Không có dữ liệu để vẽ biểu đồ ma trận cho năm {nam}.")
        return

    x_min, x_max = -4.0, 0.5
    y_min, y_max = 0.0, 5.0
    m_nguong = -1.78
    z_nguong = 1.81

    # Lấy các doanh nghiệp trong vùng hiển thị chuẩn của đề bài
    df_plot = df_nam[
        (df_nam['M_Score'] >= x_min) & (df_nam['M_Score'] <= x_max) &
        (df_nam['Z_Score'] >= y_min) & (df_nam['Z_Score'] <= y_max)
    ].copy()

    fig, ax = plt.subplots(figsize=(12, 8))

    # 1. Đổ màu nền 4 góc phần tư theo chuẩn giao diện tài chính
    # Góc trên - trái: An toàn (Xanh lục nhạt)
    ax.fill_between([x_min, m_nguong], z_nguong, y_max, color='#E8F5E9', alpha=0.6, zorder=0)
    # Góc trên - phải: Nghi vấn gian lận (Cam nhạt)
    ax.fill_between([m_nguong, x_max], z_nguong, y_max, color='#FFE0B2', alpha=0.5, zorder=0)
    # Góc dưới - trái: Nguy cơ phá sản (Vàng nhạt)
    ax.fill_between([x_min, m_nguong], y_min, z_nguong, color='#FFF9C4', alpha=0.6, zorder=0)
    # Góc dưới - phải: Khủng hoảng kép (Đỏ hồng nhạt)
    ax.fill_between([m_nguong, x_max], y_min, z_nguong, color='#FFCDD2', alpha=0.5, zorder=0)

    # 2. Ghi chú tên 4 vùng rủi ro
    ax.text(-2.9, 4.2, 'An toàn\n(Z > 2.99, M < -1.78)', fontsize=10, color='#2E7D32', ha='center', va='center', weight='bold')
    ax.text(-0.6, 4.2, 'Nghi vấn gian lận\n(Z > 1.81, M > -1.78)', fontsize=10, color='#E65100', ha='center', va='center', weight='bold')
    ax.text(-2.9, 0.8, 'Nguy cơ phá sản\n(Z < 1.81, M < -1.78)', fontsize=10, color='#F57F17', ha='center', va='center', weight='bold')
    ax.text(-0.6, 0.8, 'Khủng hoảng kép\n(Z < 1.81, M > -1.78)', fontsize=10, color='#B71C1C', ha='center', va='center', weight='bold')

    # 3. Các đường ngưỡng phân tách
    ax.axvline(x=m_nguong, color='black', linestyle='--', linewidth=1.2, zorder=2)
    ax.axhline(y=z_nguong, color='black', linestyle='--', linewidth=1.2, zorder=2)
    ax.axhline(y=2.99, color='gray', linestyle=':', linewidth=1.0, alpha=0.7, zorder=2)

    # 4. Bảng màu 4 trạng thái chuẩn theo hình mẫu PDF
    palette = {
        'An toàn': '#3F51B5',           # Xanh dương đậm
        'Nguy cơ phá sản': '#FBC02D',   # Vàng sẫm
        'Nghi vấn gian lận': '#FB8C00', # Cam
        'Khủng hoảng kép': '#C62828'    # Đỏ sẫm
    }

    # Đảm bảo thứ tự hiển thị trong Legend khớp mẫu
    hue_order = ['An toàn', 'Nguy cơ phá sản', 'Nghi vấn gian lận', 'Khủng hoảng kép']
    hue_order_present = [h for h in hue_order if h in df_plot['Trang_Thai_Rui_Ro'].unique()]

    sns.scatterplot(
        data=df_plot, x='M_Score', y='Z_Score', hue='Trang_Thai_Rui_Ro',
        hue_order=hue_order_present,
        palette=palette, s=75, edgecolor='black', linewidth=0.6, alpha=0.88, zorder=3, ax=ax
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title(f'Phân loại doanh nghiệp theo rủi ro Tài chính & Gian lận\n(Toàn sàn: {exchange} - Năm {nam})', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Beneish M-Score (Ngưỡng phân tách tại -1.78)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Altman Z-Score (Ngưỡng phân tách tại 1.81 và 2.99)', fontsize=11, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.4, zorder=0)
    ax.legend(title='Trạng thái rủi ro', loc='upper right', framealpha=0.95)

    plt.figtext(
        0.12, 0.015,
        f"* Ghi chú: Hiển thị {len(df_plot)}/{len(df_nam)} doanh nghiệp trong vùng quan sát trọng tâm (Z ∈ [0.0, 5.0], M ∈ [-4.0, 0.5]).",
        fontsize=9, fontstyle='italic', color='#424242'
    )

    duong_dan_anh = os.path.join(thu_muc_luu, f'MaTran_RuiRo_{exchange}_{nam}.png')
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(duong_dan_anh, dpi=300)
    plt.close()
    print(f"  -> Đã xuất đồ thị Ma trận 4 góc phần tư: {duong_dan_anh}")

def ve_trendline_suy_thoai(df, danh_sach_ma_cp, thu_muc_luu):
    """
    Vẽ Biểu đồ Trendline trục kép (Dual-axis) cho các doanh nghiệp suy thoái tài chính thực chất:
    - Trục trái: Altman Z-Score thể hiện sức khỏe tài chính suy giảm.
    - Trục phải: Beneish M-Score thể hiện rủi ro gian lận gia tăng.
    - Hiển thị rõ các ngưỡng cảnh báo lý thuyết Z=1.81, Z=2.99 và M=-1.78.
    """
    if not danh_sach_ma_cp:
        print("  > Không có doanh nghiệp suy thoái phù hợp để vẽ Trendline.")
        return

    for ticker in danh_sach_ma_cp:
        df_cp = df[df['Ma_CP'] == ticker].sort_values(by='Nam').dropna(subset=['Z_Score', 'M_Score'])
        if len(df_cp) < 2:
            continue

        fig, ax1 = plt.subplots(figsize=(10, 5.8))

        years = [str(int(y)) for y in df_cp['Nam']]
        z_vals = df_cp['Z_Score'].values
        m_vals = df_cp['M_Score'].values

        # 1. Trục trái: Z-Score (Màu đỏ sẫm)
        color_z = '#C62828'
        ax1.set_xlabel('Năm tài chính', fontsize=11, fontweight='bold', labelpad=8)
        ax1.set_ylabel('Altman Z-Score (Sức khỏe tài chính)', color=color_z, fontweight='bold')
        l1 = ax1.plot(years, z_vals, color=color_z, marker='o', markersize=8, linewidth=2.5, label='Z-Score (Trục trái)')
        ax1.tick_params(axis='y', labelcolor=color_z)

        # Hiển thị giá trị số tại từng điểm Z
        for x_idx, y_val in enumerate(z_vals):
            ax1.annotate(f"{y_val:.2f}", (x_idx, y_val), textcoords="offset points", xytext=(0, 9),
                         ha='center', fontsize=9, fontweight='bold', color=color_z)

        # Ngưỡng Z
        ax1.axhline(y=1.81, color=color_z, linestyle='--', alpha=0.6, linewidth=1.2, label='Ngưỡng Z=1.81 (Nguy hiểm)')
        ax1.axhline(y=2.99, color=color_z, linestyle=':', alpha=0.6, linewidth=1.2, label='Ngưỡng Z=2.99 (An toàn)')

        # Thiết lập giới hạn trục Y cho Z để đường ngưỡng luôn hiển thị rõ
        z_min_plot = min(0.0, float(np.nanmin(z_vals)) - 0.5)
        z_max_plot = max(3.5, float(np.nanmax(z_vals)) + 0.8)
        ax1.set_ylim(z_min_plot, z_max_plot)

        # 2. Trục phải: M-Score (Màu cam)
        ax2 = ax1.twinx()
        color_m = '#EF6C00'
        ax2.set_ylabel('Beneish M-Score (Rủi ro gian lận)', color=color_m, fontweight='bold')
        l2 = ax2.plot(years, m_vals, color=color_m, marker='s', markersize=8, linewidth=2.5, label='M-Score (Trục phải)')
        ax2.tick_params(axis='y', labelcolor=color_m)

        # Hiển thị giá trị số tại từng điểm M
        for x_idx, y_val in enumerate(m_vals):
            ax2.annotate(f"{y_val:.2f}", (x_idx, y_val), textcoords="offset points", xytext=(0, -14),
                         ha='center', fontsize=9, fontweight='bold', color=color_m)

        # Ngưỡng M
        ax2.axhline(y=-1.78, color=color_m, linestyle='--', alpha=0.6, linewidth=1.2, label='Ngưỡng M=-1.78 (Gian lận)')

        # Thiết lập giới hạn trục Y cho M
        m_min_plot = min(-3.5, float(np.nanmin(m_vals)) - 0.8)
        m_max_plot = max(0.5, float(np.nanmax(m_vals)) + 0.8)
        ax2.set_ylim(m_min_plot, m_max_plot)

        # Hợp nhất Legend từ 2 trục
        lines = l1 + l2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', framealpha=0.92)

        plt.title(f'XU HƯỚNG SUY THOÁI TÀI CHÍNH & GIAN LẬN: DOANH NGHIỆP {ticker}', fontsize=12, fontweight='bold', pad=15)
        ax1.grid(True, linestyle=':', alpha=0.4)

        duong_dan_anh = os.path.join(thu_muc_luu, f'Trendline_SuyThoai_{ticker}.png')
        plt.tight_layout()
        plt.savefig(duong_dan_anh, dpi=300)
        plt.close()
        print(f"  -> Đã xuất đồ thị Trendline suy thoái: {duong_dan_anh}")

def xuat_excel_bao_cao(df, exchange, nam_phan_tich, thu_muc_luu):
    """Xuất file Excel tổng hợp kết quả phân tích đầy đủ các chỉ số theo yêu cầu đề bài."""
    cols_xuat = [
        'Ma_CP', 'San', 'Nam',
        'Z_Score', 'Canh_Bao_Z',
        'M_Score', 'Canh_Bao_M',
        'Trang_Thai_Rui_Ro',
        'X1_VonLuuDong', 'X2_LNChuaPhanPhoi', 'X3_EBIT', 'X4_VCSH_No', 'X5_DoanhThu',
        'DSRI', 'GMI', 'AQI', 'SGI', 'DEPI',
        'Tong_Tai_San', 'Doanh_Thu', 'Loi_Nhuan_Sau_Thue', 'Von_Chu_So_Huu', 'No_Phai_Tra'
    ]
    cols_exist = [c for c in cols_xuat if c in df.columns]
    file_excel = os.path.join(thu_muc_luu, f'DuLieu_RuiRo_{exchange}_{nam_phan_tich}.xlsx')
    df[cols_exist].to_excel(file_excel, index=False)
    print(f"  -> Đã lưu bảng dữ liệu Excel tổng hợp: {file_excel}")