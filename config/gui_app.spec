# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# Collect data files from AI libraries
whisper_data = collect_data_files('whisper')
torch_data = collect_data_files('torch')
torchaudio_data = collect_data_files('torchaudio')

a = Analysis(
    ['../gui_app.py'],
    pathex=[],
    binaries=[
        ('../bin/ffmpeg.exe', 'bin'),
    ],
    datas=[
        ('../assets/Youtube_text.ico', 'assets'),
        ('../bin/ffmpeg.exe', 'bin'),
    ] + whisper_data + torch_data + torchaudio_data,
    hiddenimports=[
        'whisper',
        'torch',
        'torchaudio', 
        'moviepy',
        'moviepy.editor',
        'moviepy.video.io.VideoFileClip',
        'moviepy.audio.io.AudioFileClip',
        'moviepy.config',
        'yt_dlp',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'threading',
        'pathlib',
        'tempfile',
        'shutil',
        'subprocess',
        'numpy',
        'librosa',
        'librosa.core',
        'librosa.feature',
        'librosa.util',
        'scipy',
        'scipy.signal',
        'scipy.ndimage',
        'numba',
        'ffmpeg',
        'soundfile',
        'resampy'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoToTextConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../assets/Youtube_text.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='VideoToTextConverter',
)
