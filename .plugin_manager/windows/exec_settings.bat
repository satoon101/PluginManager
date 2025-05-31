@echo off

rem Store the current directory for later use
set STARTDIR=%CD%

rem Does the settings.ini file exist?
if not exist %STARTDIR%\settings.ini (
    echo No settings.ini file found.
    echo Please execute the setup.bat file to create the settings.ini before proceeding.
    exit /b 1
)

rem Get all the configuration values
for /f "eol=# delims=" %%a in (settings.ini) do (
    set "%%a"
)

rem Is PYTHON_EXECUTABLE defined in the settings?
if not defined PYTHON_EXECUTABLE (
    echo PYTHON_EXECUTABLE not defined in your settings.ini.
    exit /b 1
)
