# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Lấy tất cả dữ liệu cần thiết của ultralytics (để tránh lỗi thiếu file config của yolo)
datas = []
binaries = []
hiddenimports = ['tkinterweb', 'PIL._tkinter_finder']

# Thu thập dependencies của ultralytics
tmp_ret = collect_all('ultralytics')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Thêm model YOLO vào trong exe (Source Path, Destination Path bên trong exe)
# Lưu ý: Code của bạn đang gọi resource_path("app/models/yolov8n.pt")
# Nên ta map file thực tế vào đúng đường dẫn ảo đó.
datas.append(('app/models/yolov8n.pt', 'app/models'))

a = Analysis(
    ['app/main.py'],  # File chạy chính
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CameraTrackingAI',  # Tên file exe sau khi build
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Đặt False để tắt màn hình đen (CMD) khi chạy app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)