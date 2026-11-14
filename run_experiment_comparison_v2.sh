#!/bin/bash

echo "Running comparison experiment v2"
mkdir results_comparison_v2
source venv/bin/activate
pip install -r requirements.txt
python3 experiment_comparison_v2.py >> experiment_comparison_v2.out
