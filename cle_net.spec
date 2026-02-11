# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CLE-Net

This file is used by PyInstaller to create standalone executables for CLE-Net.
To build the executable, run:
  pyinstaller cle_net.spec
"""

block_cipher = None

a = Analysis(
    ['cle_net_cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'core',
        'core.agent',
        'core.agent.agent',
        'core.agent.atomizer',
        'core.agent.event_stream',
        'core.agent.multimodal_input',
        'core.agent.rule_engine',
        'core.agent.symbol_mapper',
        'core.agent.enhanced_symbolic_regression',
        'core.blockchain',
        'core.chain',
        'core.chain.consensus',
        'core.chain.ledger',
        'core.network',
        'core.network.p2p_node',
        'core.network.watchdog',
        'core.network.state_migration',
        'core.network.recovery',
        'core.network.byzantine',
        'core.network.incentives',
        'core.network.partition',
        'core.graph',
        'core.graph.knowledge_graph',
        'core.cosmos',
        'core.cosmos.types',
        'core.cosmos.x.cognitive',
        'core.cosmos.x.laws',
        'core.cosmos.x.consensus',
        'core.cosmos.app',
        'core.cosmos.state_machine',
        'core.cosmos.tendermint',
        'dataclasses',
        'dataclasses_json',
        'typing_extensions',
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
    name='cle-net',
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
    icon=None,
)
