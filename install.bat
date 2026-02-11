@echo off
echo CLE-Net Installer
echo ================
echo.
echo This will install CLE-Net to your system.
echo.
set /p install_dir="Enter installation directory (default: C:\CLE-Net): "
if "%install_dir%"=="" set install_dir=C:\CLE-Net

echo Creating directory: %install_dir%
mkdir "%install_dir%" 2>nul

echo Copying files...
copy "dist\cle-net.exe" "%install_dir%\" >nul
copy "README.md" "%install_dir%\" >nul
copy "LICENSE" "%install_dir%\" >nul
copy "QUICKSTART.md" "%install_dir%\" >nul

echo Creating data directory...
mkdir "%install_dir%\data" 2>nul

echo.
echo Installation completed successfully!
echo.
echo CLE-Net has been installed to: %install_dir%
echo.
echo To run CLE-Net, navigate to the installation directory and run:
echo   cle-net.exe
echo.
echo For help, run:
echo   cle-net.exe --help
echo.
pause
