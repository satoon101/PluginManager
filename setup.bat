@echo off

rem Set the start directory for later reference
set STARTDIR="%CD%"

cls

rem Does the settings file already exist?
if exist %STARTDIR%\settings.ini (

    echo settings.ini file already exists.  Please edit it to your liking.
    echo If there is an error in the file, please delete it and re-run this script.

) else (

    rem Copy the default settings
    copy .plugin_helpers\tools\settings.ini settings.ini
    echo Creating settings.ini file.  Set values to your specifications then re-execute setup.bat.
    echo You MUST have PYTHON_EXECUTABLE defined before going further.
)

rem Does the config file already exist?
if exist %STARTDIR%\config.ini (

    echo config.ini file already exists.  Please edit it to your liking.
    echo If there is an error in the file, please delete it and re-run this script.

) else (

    rem Copy the default config
    copy .plugin_helpers\tools\config.ini config.ini
    echo Creating config.ini file.  Set values to your specifications before executing any commands.
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
    goto :done
)

:done

endlocal

rem Link the prerequisite file
if not exist %STARTDIR%\prerequisites.bat (
    mklink /H %STARTDIR%\prerequisites.bat %STARTDIR%\.plugin_helpers\files\prerequisites.bat
)

rem Link all of the helper batch scripts
for %%F in (".plugin_helpers\packages\*.py") do (
    if not "%%~nxF"=="__init__.py" (
        if not exist %STARTDIR%\%%~nF.bat (
            mklink /H %STARTDIR%\%%~nF.bat %STARTDIR%\.plugin_helpers\files\caller.bat
        )
    )
)

pause
