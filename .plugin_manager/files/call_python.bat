@echo off

rem Execute the configuration
call .plugin_helpers/files/exec_settings

rem Did the configuration encounter no errors?
if %errorlevel% == 0 (

    rem Call the given package
    %PYTHON_EXECUTABLE% %STARTDIR%\.plugin_helpers\packages\%~n1.py
)
