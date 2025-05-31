@echo off

rem Execute the settings
call exec_settings

rem Did the settings encounter errors?
if %errorlevel% == 0 (
    %PYTHON_EXECUTABLE% -m pip install --upgrade pip
    %PYTHON_EXECUTABLE% -m pip install --upgrade -r .plugin_manager/tools/requirements.txt
)
pause
