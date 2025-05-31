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

rem Link the prerequisite file
if not exist %STARTDIR%\prerequisites.bat (
    mklink /H %STARTDIR%\prerequisites.bat %STARTDIR%\.plugin_manager\files\prerequisites.bat
)

rem Link all of the helper batch scripts
for %%F in (".plugin_manager\packages\*.py") do (
    if not "%%~nxF"=="__init__.py" (
        if not exist %STARTDIR%\%%~nF.bat (
            mklink /H %STARTDIR%\%%~nF.bat %STARTDIR%\.plugin_manager\files\caller.bat
        )
    )
)

pause
