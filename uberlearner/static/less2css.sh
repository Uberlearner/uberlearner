#!/bin/bash

PWD=$(printf "%q" "$(pwd)")
LESS_FOLDER=$PWD"/less"
CSS_FOLDER=$PWD"/css"
BOOTSTRAP_SRC=$LESS_FOLDER"/bootstrap.less"
RESPONSIVE_SRC=$LESS_FOLDER"/responsive.less"
BOOTSTRAP_TARGET=$CSS_FOLDER"/bootstrap.css"
RESPONSIVE_TARGET=$CSS_FOLDER"/bootstrap-responsive.css"

lessc -x "$BOOTSTRAP_SRC" > "$BOOTSTRAP_TARGET"
lessc -x "$RESPONSIVE_SRC" > "$RESPONSIVE_TARGET"

echo "Conversion Completed..."