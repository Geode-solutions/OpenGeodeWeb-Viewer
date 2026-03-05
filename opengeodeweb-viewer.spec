# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []
datas += collect_data_files('opengeodeweb_viewer')
tmp_ret = collect_all('vtkmodules')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src/opengeodeweb_viewer/app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

to_exclude = [
    'opengl32',
    'opengl32sw',
    'libEGL',
    'libGLESv2',
    'libX11',
    'libXext',
    'libXrender',
    'libXcursor',
    'libXfixes',
    'libXi',
    'libXinerama',
    'libXrandr',
    'libXcomposite',
    'libXdamage',
    'libXxf86vm',
    'libxcb',
    'libxkbcommon',
    'libwayland',
]
a.binaries = TOC([
    entry for entry in a.binaries
    if not any(
        entry[0].lower().startswith(prefix.lower())
        for prefix in to_exclude
    )
])

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='opengeodeweb-viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
