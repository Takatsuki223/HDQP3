# -*- mode: python ; coding: utf-8 -*-

import os
import shutil

block_cipher = None
# 打包数据文件
datas = [('river.jpg', '.')]

a = Analysis(
    ['screenshot.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['bs4', 'requests', 'urllib3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    distpath='XiJiang_Water_level',  # 输出目录名称
    workpath='build',    # 工作目录名称
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='水位数据爬取',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台，方便查看运行状态
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
