@echo off
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."
set SCRIPT_DIR=%cd%
set SCRIPT_NAME=main.py
set EXECUTABLE_NAME=SeedingScript.exe
set ZIP_NAME=SeedingScript.zip
set MODEL_DATA_DIR=model_data

rem Install PyInstaller if needed
pip install pyinstaller

rem Compile the script into an executable
:: pyinstaller --onefile --noconsole --add-data "C:\Program Files\Tesseract-OCR;Tesseract-OCR" --collect-all easyocr --name %EXECUTABLE_NAME% --hidden-import=skimage.exposure %SCRIPT_NAME%
:: pyinstaller --onefile --noconsole --add-data "C:\Users\mrkal\.EasyOCR;Easy-OCR" --collect-all easyocr --name %EXECUTABLE_NAME% --hidden-import=skimage.exposure %SCRIPT_NAME%
:: pyinstaller --onefile --noconsole --collect-all easyocr --name %EXECUTABLE_NAME% --hidden-import=skimage.exposure %SCRIPT_NAME%

del %EXECUTABLE_NAME%.spec

rem Create a zip file of the compiled executable using tar.exe
cd .\dist
tar.exe -c -a -f "%ZIP_NAME%" .\%EXECUTABLE_NAME% %MODEL_DATA_DIR%

echo.
echo %EXECUTABLE_NAME% has been compiled and %ZIP_NAME% has been created.
echo.