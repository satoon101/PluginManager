@echo off

rem Store the current directory for later use
set STARTDIR=%CD%
set ERROR_LEVEL=0

rem Does the settings.ini file exist?
if not exist %STARTDIR%\settings.ini (
    echo No settings.ini file found.
    echo Please execute the setup.bat file to create the settings.ini before proceeding.
    exit 1
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

@echo off

setlocal enabledelayedexpansion

rem Define the repository root
set REPO_ROOT=%CD%

rem Path to the .gitmodules file
set GITMODULES_FILE=%REPO_ROOT%\.gitmodules

rem Check if the .gitmodules file exists
if not exist "%GITMODULES_FILE%" (
    echo No .gitmodules file found.
    exit /b 1
)

rem Extract only the path value and trim leading space
for /f "tokens=2 delims==" %%A in ('findstr /R "^ *path =" "%GITMODULES_FILE%"') do (
    set SUBMODULE_DIRECTORY=%%A
    set SUBMODULE_DIRECTORY=!SUBMODULE_DIRECTORY:~1!
    cls
    setx SUBMODULE_DIRECTORY "!SUBMODULE_DIRECTORY!"
    cls
    goto :done
)

:done

endlocal
