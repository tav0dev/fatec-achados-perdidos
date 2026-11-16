@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 (
    echo ERRO: Nao foi possivel acessar a pasta do projeto.
    pause
    exit /b 1
)
echo.
echo  Achados e Perdidos - Fatec Itapetininga
echo  Gustavo Cuba de Oliveira e Lauren Gabriel de Campos
echo.
call "scripts\python_env.bat"
if not defined ACHADOS_PORT set "ACHADOS_PORT=5057"
set "PYTHONUTF8=1"
if not exist "%ACHADOS_PYTHON%" (
    echo Criando ambiente Python no disco local do Windows...
    where py >nul 2>nul
    if errorlevel 1 (
        python -m venv "%ACHADOS_ENV%"
    ) else (
        py -3 -m venv "%ACHADOS_ENV%"
    )
    if errorlevel 1 goto :venv_error
)
"%ACHADOS_PYTHON%" -c "import flask, pymongo, reportlab" >nul 2>nul
if errorlevel 1 (
    echo Instalando bibliotecas. E necessario acesso a internet na primeira vez.
    "%ACHADOS_PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 goto :install_error
)
"%ACHADOS_PYTHON%" manage.py init
if errorlevel 1 goto :mongo_error
echo.
echo Abra http://127.0.0.1:%ACHADOS_PORT% no navegador.
echo Para encerrar, pressione Ctrl+C nesta janela.
echo.
"%ACHADOS_PYTHON%" app.py
pause
popd
exit /b
:venv_error
echo ERRO: Nao foi possivel criar o ambiente Python em %ACHADOS_ENV%.
echo Confira o erro acima. Se Python estiver instalado, verifique a permissao de escrita.
pause
popd
exit /b 1
:install_error
echo ERRO: Nao foi possivel instalar as bibliotecas. Confira sua conexao com a internet.
pause
popd
exit /b 1
:mongo_error
echo ERRO: Inicie MongoDB Server em Servicos do Windows.
echo No Compass, teste a conexao mongodb://localhost:27017 e execute este arquivo novamente.
pause
popd
exit /b 1
