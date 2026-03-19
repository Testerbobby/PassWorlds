@echo off
echo Building PassWorlds for Windows...
echo.

pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building GUI version...
pyinstaller --onefile --windowed --name PassWorlds_GUI password_generator_ui.py

echo.
echo Building CLI version...
pyinstaller --onefile --name PassWorlds_CLI password_generator.py

echo.
echo ========================================
echo Build complete! Executables in dist folder:
echo   - dist\PassWorlds_GUI.exe
echo   - dist\PassWorlds_CLI.exe
echo ========================================
pause
