# JobTrendX
An application for job ad analysis

## Project scope: Analyzing the job ads from different sources, to analyzing and visualizing the job trends and requirements in the market.
The project is starting with looking at the StepStone's job ads and than it will move forward to other sources and sites.


### Data structure:
* It get the jobs from a source (yet not sure!)
* Analysis the requirement sections
* Analysis the benefits, location, salary, ...
* Processing pipelines
* keyword tracking
* Indexing

# Structure:
    JobTrendX/
    │-- data/                 # Store raw .eml files here
    │-- configs/              # Hydra configuration files (YAML)
    │   ├── config.yaml        # Main config file
    │-- src/                   # Source code directory
    │   ├── __init__.py         # Makes the folder a package
    │   ├── main.py             # Main entry point for the app
    │   ├── email_processor.py  # Module to handle .eml parsing
    │   ├── analysis.py         # Module for analyzing job requirements
    │   ├── visualization.py    # Module for reporting/visualization
    │-- tests/                 # Unit tests for different components
    │-- README.md              # Project overview and plan
    │-- requirements.txt       # Dependencies (Hydra, email, pandas, etc.)
    │-- .gitignore             # Ignore unnecessary files (e.g., .env, data/)
    │-- setup.py               # Optional, for packaging the app
