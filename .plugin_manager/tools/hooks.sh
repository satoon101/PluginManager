# Store the current directory for later use
STARTDIR="$PWD"

# Windows?
if [ "$OSTYPE" == "msys" ]; then
    DIRECTORY='windows'
    EXTENSION='bat'

# Linux
else
    DIRECTORY='linux'
    EXTENSION='sh'
fi

# Copy the config.ini file
if [ ! -f $STARTDIR/config.ini ]; then
    cat ".plugin_manager/tools/config.ini" ".plugin_manager/$DIRECTORY/config.ini" > "$STARTDIR/config.ini"
fi

# Link the prerequisite file if it doesn't exist
if [ ! -f $STARTDIR/prerequisites.$EXTENSION ]; then
    ln ./.plugin_manager/$DIRECTORY/prerequisites.$EXTENSION $STARTDIR/prerequisites.$EXTENSION
fi

# Loop through all Python files
for filename in ./.plugin_manager/packages/*.py; do

    # Skip the __init__ file
    if [ "$(basename "${filename%.**}")" == "__init__" ]; then
        continue
    fi

    # Has the link file not been created?
    if [ ! -f ./"$(basename "${filename%.*}")".$EXTENSION ]; then

        # Link a caller for the file
        ln ./.plugin_manager/$DIRECTORY/caller.$EXTENSION ./"$(basename "${filename%.*}")".$EXTENSION
    fi
done
