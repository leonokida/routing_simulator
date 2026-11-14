#!/bin/bash

echo "Running optimization dataset"
source venv/bin/activate
pip install -r requirements.txt
python3 optimization_dataset.py >> optimization_dataset.out