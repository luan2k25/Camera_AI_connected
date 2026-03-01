# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

# =========================================================
# 1. CẤU HÌNH CÁC THƯ VIỆN KHÓ TÍNH (ULTRALYTICS, TKINTERWEB)
# =========================================================

# Ultralytics cần thu thập toàn bộ config, assets đi kèm mới chạy được
datas = []
binaries = []
hiddenimports = ['tkinterweb', 'PIL._tkinter_finder']

# Hàm collect_all giúp lấy hết dependencies của ultralytics
tmp_ret = collect_all('ultralytics')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# =========================================================
# 2. CẤU HÌNH FILE ASSETS CỦA BẠN (MODEL)
# =========================================================

# Định nghĩa đường dẫn file model cần nhúng vào trong EXE
# Cú pháp: ('đường_dẫn_file_gốc', 'đường_dẫn_trong_exe')
# Code của bạn gọi: resource_path("app/models/yolov8n.pt")
# Nên ta phải đặt nó vào thư mục "app/models" bên trong exe.
my_datas = [
    ('app/models/yolov8n.pt', 'app/models'),
]

datas += my_datas

# =========================================================
# 3. THIẾT LẬP BUILD
# =========================================================

block_cipher = None

a = Analysis(
    ['app/main.py'],           # File chạy chính nằm trong folder app
    pathex=['app'],                 # Đường dẫn tìm kiếm module (để trống nó tự tìm từ root)
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TrackingApp',        # Tên file EXE output
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,              # ĐỂ TRUE ĐỂ DỄ DEBUG (Sau này chạy ngon thì sửa thành False để ẩn console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TrackingApp',
)