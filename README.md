# Tracking-Enrichment-GTM-Analysis-Script
This repository contains a Python workflow that analyzes Google Tag Manager (GTM) containers, compares environments, and highlights potential issues such as misconfigured variables, missing tags, and authentication problems.
One of the key requirements for running the script is generating a Google OAuth2 token, which grants access to the GTM API.
A Python-based tool to analyze and validate Google Tag Manager (GTM) configurations. 

![python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![gtm-api](https://img.shields.io/badge/Google%20API-Tag%20Manager-green.svg)
![status](https://img.shields.io/badge/Status-Active-success.svg)



## Overview
The GTM Analysis Toolkit automates the validation of GTM container structures by connecting to the Google Tag Manager API. 
It extracts configuration data from the container, processes it, and compares environments such as Workspace vs Live to surface potential issues.

## Features
This script performs the following tasks:
- Connects to the Google Tag Manager API using OAuth2 authentication
- Downloads and compares:
  - Tags
  - Triggers
  - Variables
  - Built-in variables
- Check the LIVE GTM container with another version (or workspace)
- Produces structured output identifying missing consents and errors
- Supports local execution via Jupyter Notebook (as provided in this repository)

The goal is to automate the detection of GTM inconsistencies before publishing updates.




## Requirements
Before running the script, ensure you have:
-   Python 3.9+
-   GTM access\
-   Tag Manager API enabled
-   The following packages (installed automatically in the notebook):
  -   google-auth
  -   google-auth-oauthlib
  -   google-api-python-client
  -   requests, urllib3, httplib2
  -   PyYAML

The notebook will install missing dependencies at runtime.


## Installation

    git clone https://github.com/<your-org>/<your-repo>.git
    cd <your-repo>
    jupyter notebook tracking_enrich_GTM.ipynb



##  Generating the OAuth Token
To access GTM programmatically, the script uses InstalledAppFlow, which requires a Google OAuth client configuration.

1.  Create a Google Cloud project\
  Go to: https://console.cloud.google.com/
  Select an existing project or create a new one.

2.  Enable Tag Manager API\
  Make sure the Tag Manager API is enabled
  APIs & Services → Enabled APIs & Services → Enable API
  Search for Tag Manager API and enable it.

3.  Create OAuth Desktop App credentials\
  Go to APIs & Services → Credentials → Create Credentials → OAuth client ID
  Choose: Application type: Desktop app
  Download the generated file — usually named: client_secret_<random>.json
  Save it in the same directory as the notebook, and rename it to: client_secrets.json


## Authenticate for the First Time

The first time you run:

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['https://www.googleapis.com/auth/tagmanager.edit.containers']
)
credentials = flow.run_local_server(port=0)

A browser window opens—log in and confirm access.
A file named token.json will be created.
Next runs reuse this token automatically.


## Configuration

Edit the variables in the notebook:

GTM_ACCOUNT_ID = "123456789"
GTM_CONTAINER_ID = "abc123"
WORKSPACE_ID = "1"

You can retrieve these from the GTM interface URL:

https://tagmanager.google.com/#/container/accounts/<ACCOUNT>/containers/<CONTAINER>/workspaces/<WORKSPACE>


## Running the Analysis

1.  Install dependencies\
2.  Authenticate\
3.  Fetch GTM data\
4.  Compare workspace vs live\
5.  Inspect results
   

## Output

-   JSON comparison\
-   Diff of tags, triggers, variables\
-   Missing or inconsistent items


## Troubleshooting

-   Ensure OAuth credentials are correct\
-   Ensure your Google account has GTM edit rights\
-   Delete `token.json` to re-authenticate


## Contributing

Fork → Branch → Pull Request


## License

MIT License



