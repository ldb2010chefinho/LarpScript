@echo off
chcp 65001 >nul
echo Instalando as cores da LARP Script no VS Code...
xcopy /E /I /Y "%~dp0larp-vscode" "%USERPROFILE%\.vscode\extensions\ldb.larp-script-0.1.0" >nul
if errorlevel 1 (
  echo Deu erro ao copiar. Confira se a pasta larp-vscode esta ao lado deste arquivo.
) else (
  echo Pronto! Feche o VS Code por completo e abra de novo.
)
pause
