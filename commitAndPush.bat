@echo off
rem Change the remote name and branch name as needed
set REMOTE=origin
set BRANCH=main

rem Add all files to the staging area
git add .

rem Check if there are any changes to commit
git diff --quiet --staged
if %errorlevel% equ 0 (
  echo No changes to commit
  goto :end
)

rem Commit with a default message
git commit -m "Auto commit"

rem Push to the remote repository
git push %REMOTE% %BRANCH%

:end
pause
