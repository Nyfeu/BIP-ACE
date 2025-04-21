@echo off
setlocal enabledelayedexpansion

:: 1. Instalar dependências
pip install -r requirements.txt
pip install pyinstaller pillow

:: 2. Converter ícone para .ico
python -c "from PIL import Image; Image.open('assets/edit.png').resize((256,256)).save('assets/edit.ico')"

:: 3. Buildar executável
pyinstaller --noconfirm --clean --onefile --windowed --icon=assets/edit.ico --name BIP-ACE main.py

:: 4. Criar pasta de distribuição
set "dist_dir=pkg"
rmdir /S /Q "!dist_dir!" 2>nul
mkdir "!dist_dir!"

:: 5. Copiar arquivos necessários
copy "dist\BIP-ACE.exe" "!dist_dir!" >nul
xcopy /E /I /Y "assets" "!dist_dir!\assets" >nul
xcopy /E /I /Y "configs" "!dist_dir!\configs" >nul
xcopy /E /I /Y "examples" "!dist_dir!\examples" >nul

:: 6. Criar ZIP final
powershell Compress-Archive -Path "!dist_dir!\*" -DestinationPath "BIP-ACE.zip" -Force

:: 7. Limpeza
rmdir /S /Q dist build __pycache__ 2>nul
del BIP-ACE.spec 2>nul

echo.
echo ==============================================
echo Build completo! Arquivo BIP-ACE.zip gerado!
echo ==============================================
echo.
pause