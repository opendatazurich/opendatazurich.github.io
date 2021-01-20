#!/bin/bash

[ ! -d pyenv ] && python3 -m venv pyenv
source pyenv/bin/activate

pip3 install --upgrade pip
pip3 install -r automation-requirements.txt
