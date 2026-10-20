@echo off
chcp 65001 >nul
py "%~dp0tests\rodar_testes.py" %*
