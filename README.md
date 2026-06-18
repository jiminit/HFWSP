# HFWSP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

## Overview

This is the full build for the Australian lifetime risk of CVD website (https://hfwsp.onrender.com/).
The site is hosted on Render and deployed using gunicorn.

## Directory Structure

```text
HFWSP/
├── hfwsp/                  # Core code and functions
│   ├── app.py              # Main app file
│   ├── errorcheck.py       # Hosts function that checks user inputs for errors
│   ├── life_table.py       # Hosts life table functions
│   ├── plots.py            # Plot functions
│   ├── rfs_and_tps.py      # Uses user inputs to calculate transition probabilities for the models
│   ├── tps.csv             # Base transition probabilities
│   ├── rfs.csv             # Base risk factor trajectories
├── static/                 # html and css files
├── requirements.txt        # Package dependencies
└── README.md               # Repository documentation
```


## Questions or suggestions?
Contact: Jedidiah Morton (jedidiah.morton@monash.edu.au)
