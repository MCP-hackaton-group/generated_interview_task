@echo off
REM Run the Interview Task Generator Server

echo ========================================================
echo    Technical Interview Task Generator Server
echo ========================================================
echo.
echo This server integrates:
echo  - Jira Extractor Agent
echo  - Manager Prompt Agent 
echo  - Task Generator Agent
echo.
echo The API will be available at http://localhost:5001/user-message
echo.
echo HOW TO USE:
echo -----------
echo 1. Keep this window open while using the API
echo 2. Send a POST request to http://localhost:5001/user-message with this format:
echo    {
echo      "message": {
echo        "task_description": "backend development, authentication, etc",
echo        "language": "Python, React, etc"
echo      }
echo    }
echo.
echo 3. Final assignments are saved to the 'results' directory
echo    as 'api_result_[timestamp].json'
echo.
echo Starting server...
echo.

cd "%~dp0"
mkdir results 2>nul
python server/api/index.py

pause
