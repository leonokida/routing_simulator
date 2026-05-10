#!/bin/bash

echo "Running comparison experiment"
mkdir results_comparison
source venv/bin/activate
pip install -r requirements.txt
python3 experiment_comparison.py >> experiment_comparison.out
