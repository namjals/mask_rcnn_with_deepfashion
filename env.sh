#!/bin/bash
export SERVICE_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$SERVICE_HOME/Mask_RCNN:$PYTHONPATH

if [ ! -d Deepfashion2 ]; then
    mkdir -p Deepfashion2
fi
