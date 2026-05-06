# marcus.spec

block_cipher = None

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(os.getcwd())

a = Analysis(
    ['backend/gui.py'],   # entry point
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[
        ('frontend', 'frontend'),
        ('pics', 'pics'),
        ('backend/marcus/memory.json', 'backend/marcus'),
        ('backend/.env', 'backend'),
    ],
    hiddenimports=[
        'groq',
        'elevenlabs',
        'speech_recognition',
        'pyaudio',
        'tkinter',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Marcus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # change to True if debugging
    icon='pics/logo.ico' if Path('pics/logo.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Marcus',
)