#!/usr/bin/env bash

# Determine the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Construct the path to ../data/todo.json
FILE_PATH="$(realpath "${SCRIPT_DIR}/../data/todo.json")"

# Check if the file exists
if [[ ! -f "$FILE_PATH" ]]; then
    echo "Todo file not found at $FILE_PATH" >&2
    exit 1
fi

# Overwrite the file with an empty JSON object
echo "{}" > "$FILE_PATH"

echo "File '$FILE_PATH' has been cleared and overwritten with {}."
