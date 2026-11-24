@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 goto hata
)
".venv\Scripts\python.exe" -c "import streamlit, numpy, PIL" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto hata
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
if errorlevel 1 goto calisma_hatasi
exit /b 0
:hata
echo Kurulum basarisiz. Python ve internet baglantisini kontrol et.
pause
exit /b 1
:calisma_hatasi
echo Uygulama baslatilamadi. Yukaridaki hata mesajini kontrol et.
pause
exit /b 1
