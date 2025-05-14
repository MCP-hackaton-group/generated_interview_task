@echo off
echo ==================================================
echo       Manager Prompt Agent - Job Requirements
echo ==================================================
echo.
echo This tool will help you create job requirements for 
echo technical home assignments through a streamlined
echo conversation - only 2 rounds of questions!
echo.
echo The AI will:
echo - Ask a few questions in the first round
echo - Follow up with one more round of questions
echo - Automatically generate the JSON file after the second round
echo - Make smart assumptions for any missing information
echo.

REM Check if the server is running, if not start it
echo Checking if AI service is running...
curl -s http://localhost:5000/health >nul
if %errorlevel% neq 0 (
    echo Starting AI service in a new window...
    echo Please wait, this may take a moment...
    start "AI Prompt Agent" cmd /c "python mcpServer_managerPrompt.py"
    
    REM Wait for server to start
    echo Waiting for AI service to initialize...
    timeout /t 8 >nul
)

echo.
echo ==================================================
echo           Starting Friendly Conversation
echo ==================================================
echo.
echo TIP: Start by describing the role and key skills
echo in your own words. The assistant will guide you 
echo through the rest of the process with just a few
echo focused questions.
echo.

REM Run the Manager Prompt Client
python managerPrompt.py

echo.
pause
