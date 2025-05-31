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
    copy .plugin_manager\tools\settings.ini settings.ini
    echo Creating settings.ini file.  Set values to your specifications then re-execute setup.bat.
    echo You MUST have PYTHON_EXECUTABLE defined before going further.
)

echo.
echo.

rem Loop through all hooks
for %%i in (.\.plugin_manager\hooks\*.*) do (

    rem Create the hook if it needs created
    if not exist %STARTDIR%\.git\hooks\%%~ni (

        mklink /H %STARTDIR%\.git\hooks\%%~ni %%i
    )
)

rem Get the current git branch
for /f %%a in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%a

rem Force a checkout to execute the checkout hook
git checkout %CURRENT_BRANCH%

pause
