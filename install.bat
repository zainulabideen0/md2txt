@echo off
title Markdown Converter Setup

echo Checking for Python installation...
python --version >nul 2>&1

:: If Python is found, skip down to installing dependencies
IF %ERRORLEVEL% EQU 0 GOTO :INSTALL_DEPS

:: If Python is not found, prompt the user
echo.
echo [WARNING] Python is not installed or not found in your system PATH.
echo Python is required to run this application.
echo.
set /p choice="Would you like to automatically install Python now? (Y/N): "

IF /I "%choice%"=="Y" GOTO :INSTALL_PYTHON

echo.
echo Installation cancelled. The app cannot run without Python.
pause
exit

:INSTALL_PYTHON
echo.
echo Installing Python via Windows Package Manager (winget)...
echo Please wait, this may take a few minutes. You may see a User Account Control (Admin) prompt.
winget install -e --id Python.Python.3.11 --scope machine

echo.
echo ========================================================
echo SUCCESS: Python has been installed!
echo ========================================================
echo IMPORTANT: To use Python, Windows needs to refresh its environment variables.
echo Please press any key to close this window, then double-click this .bat file again to finish setup!
pause
exit

:INSTALL_DEPS
echo Python is installed! 
echo ==========================================
echo Checking and installing dependencies...
echo ==========================================
python -m pip install markdown beautifulsoup4 PyQt6

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo You may now close this window and use the program.
pause