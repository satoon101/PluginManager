@echo off

rem Execute the configuration
call .plugin_manager/windows/exec_settings

rem Did the configuration encounter no errors?
if %errorlevel% == 0 (

    rem Call the given package
    %PYTHON_EXECUTABLE% %STARTDIR%\.plugin_manager\packages\%~n1.py
)
pause