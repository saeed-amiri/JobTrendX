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
        ├── data                                # Store raw .eml files here
        │   └── test.eml                        # Ignored
        ├── environment.yml                     # Conda
        ├── outputs                             # Hydra outputs. Ignored
        ├── README.md                           # Project overview and plan
        ├── requirements.txt                    # Dependencies (Hydra, email, pandas, etc.)
        ├── setup.py                            # For packaging the app
        ├── src                                 # Makes the folder a package
        │   ├── __init__.py                     # Makes the folder a package
        │   ├── main.py                         # Main entry point for the app
        │   ├── email_processor.py              # Module to handle .eml parsing
        │   ├── analysis.py                     # Module for analyzing job requirements
        │   └── visualization.py                # Module for reporting/visualization
        │   ├── conf                            # Hydra configuration files (YAML)
        │   │   ├── config.yaml                 # Main config file
        │   │   └── defaults
        │   │       ├── analysis.yaml
        │   │       ├── email_processing.yaml
        │   │       ├── hydra.yaml
        │   │       ├── paths.yaml
        │   │       └── visualization.yaml
        │── .gitignore                          # Ignore unnecessary files (e.g., .env, data/)
        └── tests                               # Unit tests for different components
