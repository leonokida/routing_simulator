#!/bin/bash

echo "Training ML model"
source venv/bin/activate
pip install -r requirements.txt
python3 train_model.py >> train_model.out