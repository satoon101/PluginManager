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

rem Does the config file already exist?
if exist %STARTDIR%\config.ini (

    echo config.ini file already exists.  Please edit it to your liking.
    echo If there is an error in the file, please delete it and re-run this script.

) else (

    rem Copy the default config
    copy .plugin_manager\tools\config.ini config.ini
    echo Creating config.ini file.  Set values to your specifications before executing any commands.
)

echo.
echo.

rem Loop through all hooks
for %%i in (.\.plugin_helpers\hooks\*.*) do (

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
