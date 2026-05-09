#!/bin/bash

echo "Running experiment"
mkdir results
source venv/bin/activate
pip install -r requirements.txt
python3 experiment.py >> experiment.out
