# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui_tkinter.py'],
             pathex=['C:\\Users\\danie\\OneDrive\\Cours\\9e session\\PI4\\Dev\\Git\\PI4P5'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='gui_tkinter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
