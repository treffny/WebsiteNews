#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run the initial news scraping to generate the first report
python generate_and_push_report.py

# Message
echo "Setup complete! The AI News website is ready to run."

