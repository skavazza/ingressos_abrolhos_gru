# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file para Abrolhos Ingressos
Uso: pyinstaller abrolhos_ingressos.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'sqlalchemy',
        'sqlalchemy.ext.declarative',
        'pandas',
        'openpyxl',
        'bcrypt',
        'models',
        'models.database',
        'models.services',
        'views',
        'views.login_dialog',
        'views.main_window',
        'views.dashboard_tab',
        'views.empresas_tab',
        'views.embarcacoes_tab',
        'views.precos_tab',
        'views.registros_tab',
        'views.relatorios_tab',
        'utils',
        'utils.validators',
        'utils.gru_automation',
        'selenium',
        'webdriver_manager',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AbrolhosIngressos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sem console (GUI only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
