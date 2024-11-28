# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['fillMastergame.py'],
    pathex=[],
    binaries=[],
    datas=[('images/fillMasterBG.png', 'images'), ('images/fillMasterIcon.png', 'images'), ('images/main_button.PNG', 'images'), ('bgm/bgm.mp3', 'bgm'), ('bgm/click sound for color buttons.mp3', 'bgm'), ('bgm/click.mp3', 'bgm'), ('bgm/game over sound.mp3', 'bgm'), ('bgm/win sound.mp3', 'bgm'), ('images/font.ttf', 'images')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='fillMastergame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
