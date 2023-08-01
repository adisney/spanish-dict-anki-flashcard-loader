#!/bin/zsh

local DEST=/opt/python_dist

pyinstaller $1 --noconfirm
APP_NAME=`echo $1 | cut -d '.' -f 1`
echo "Copying dist to $DEST"
cp -r dist/$APP_NAME $DEST
