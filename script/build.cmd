@echo off
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."
set SCRIPT_DIR=%cd%
set SCRIPT_NAME=main.py
set OUTPUT_NAME=SeedingScript.exe
set ZIP_NAME=SeedingScript.zip

rem Install PyInstaller if needed
pip install pyinstaller

rem Compile the script into an executable
pyinstaller --onefile --noconsole --add-data "C:\Program Files\Tesseract-OCR;Tesseract-OCR" --collect-all easyocr --name %OUTPUT_NAME% --hidden-import=skimage.exposure %SCRIPT_NAME%

rem SeedingScript.exe.spec

rem Create a zip file of the compiled executable using tar.exe
tar.exe -c -a -f ".\dist\%ZIP_NAME%" ".\dist\%OUTPUT_NAME%"

echo.
echo %OUTPUT_NAME% has been compiled and %ZIP_NAME% has been created.
echo.