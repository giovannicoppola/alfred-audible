#!/bin/sh
# Runs in Terminal from the workflow folder (Alfred env vars are not available
# here, so the data folder path is derived from the bundle id in info.plist).
BUNDLE_ID=$(/usr/libexec/PlistBuddy -c "Print :bundleid" info.plist)
VENV_PY="$HOME/Library/Application Support/Alfred/Workflow Data/$BUNDLE_ID/venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo "audible-cli is not installed yet — run audible:setup in Alfred first."
    exit 1
fi
exec "$VENV_PY" -m audible_cli quickstart
