#!/bin/bash

PWD=$(printf "%q" "$(pwd)")
LESS_FOLDER=$PWD"/static/less"
CSS_FOLDER=$PWD"/static/css"
BOOTSTRAP_SRC=$LESS_FOLDER"/bootstrap.less"
RESPONSIVE_SRC=$LESS_FOLDER"/responsive.less"
BOOTSTRAP_TARGET=$CSS_FOLDER"/bootstrap.css"
RESPONSIVE_TARGET=$CSS_FOLDER"/bootstrap-responsive.css"

if [ ! -d "$CSS_FOLDER" ]; then
    echo "CSS directory doesn't exist... creating"
    mkdir -p "$CSS_FOLDER"
fi

lessc -x "$BOOTSTRAP_SRC" > "$BOOTSTRAP_TARGET"
lessc -x "$RESPONSIVE_SRC" > "$RESPONSIVE_TARGET"

echo "Conversion Completed..."