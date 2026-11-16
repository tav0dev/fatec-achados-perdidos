@echo off
setlocal
pushd "%~dp0"
if errorlevel 1 exit /b 1
call "scripts\python_env.bat"
if not exist "%ACHADOS_PYTHON%" (
    echo Execute iniciar.bat primeiro para criar o ambiente Python.
    pause
    popd
    exit /b 1
)
"%ACHADOS_PYTHON%" -m pip install -r requirements-dev.txt
if errorlevel 1 (
    popd
    exit /b 1
)
"%ACHADOS_PYTHON%" -m unittest discover -s tests -v
set "ACHADOS_TEST_EXIT=%ERRORLEVEL%"
pause
popd
exit /b %ACHADOS_TEST_EXIT%
