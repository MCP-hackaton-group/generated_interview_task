@echo off
REM Script to open and list the results directory

echo ========================================================
echo    Technical Interview Task Generator - Results
echo ========================================================
echo.

set RESULTS_DIR=%~dp0results

if not exist "%RESULTS_DIR%" (
    echo No results directory found!
    echo Run one of the following scripts first:
    echo   - run_server.bat
    echo   - demo_workflow.py
    echo   - test_workflow.py
    echo   - test_api.py
    echo.
    pause
    exit /b
)

echo Found results directory at:
echo %RESULTS_DIR%
echo.

echo Latest generated assignments:
echo ----------------------------
dir /b /o-d "%RESULTS_DIR%\*assignment*.json" "%RESULTS_DIR%\*api_result*.json" 2>nul | findstr /i "\.json$"

echo.
echo Opening results folder...
explorer "%RESULTS_DIR%"

pause
