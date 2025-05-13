@echo off
echo Running Home Assignment Generator with mock data...

python clientTaskGenerate.py ^
  --jira mock_data\jira_tasks.json ^
  --prompt mock_data\prompt.json ^
  --template mock_data\template_repo.json ^
  --output mock_data\generated_assignment.json ^
  --display

echo Done!
pause
