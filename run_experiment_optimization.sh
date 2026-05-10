#!/bin/bash

echo "Running optimization experiment"
mkdir results_optimization
source venv/bin/activate
pip install -r requirements.txt
python3 experiment_optimization.py >> experiment_optimization.out