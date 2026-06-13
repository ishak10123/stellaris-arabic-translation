@echo off
:: Request administrator privileges because game directories under Program Files need admin write permissions
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto :run ) else ( goto :get_admin )

:get_admin
echo Requesting administrator privileges...
powershell -Command "Start-Process -FilePath '%0' -Verb RunAs"
exit /b

:run
python "%~dp04_auto_inject.py"
pause
