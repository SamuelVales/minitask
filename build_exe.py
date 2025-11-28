"""
Skript pro vytvoření spustitelného EXE souboru z MiniTask aplikace
"""

import PyInstaller.__main__
import os

# Získání cesty k aktuálnímu adresáři
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, 'minitask.py')

# Parametry pro PyInstaller
PyInstaller.__main__.run([
    script_path,
    '--name=MiniTask',
    '--onefile',  # Vytvoří jeden EXE soubor
    '--windowed',  # Bez konzole (GUI aplikace)
    '--clean',
    '--noconfirm',
    '--strip',  # Odstraní debug symboly (zmenší velikost)
    '--noupx',  # Vypne UPX (může způsobovat problémy s antivirem)
    '--exclude-module=numpy',  # Vyloučení nepotřebných modulů
    '--exclude-module=pandas',
    '--exclude-module=matplotlib',
    '--exclude-module=PIL',
    '--exclude-module=scipy',
    '--exclude-module=setuptools',
    '--exclude-module=pkg_resources',
    f'--distpath={os.path.join(current_dir, "dist")}',
    f'--workpath={os.path.join(current_dir, "build")}',
    f'--specpath={current_dir}',
])

print("\n" + "="*60)
print("✓ EXE soubor byl úspěšně vytvořen!")
print(f"✓ Umístění: {os.path.join(current_dir, 'dist', 'MiniTask.exe')}")
print("="*60)
