# ReSync

## About
ReSync is an open-acess tool to align intracerebral recordings (from DBS electrodes) with external recordings. A manuscript describing ReSync's functionality and methodology will follow.

This repo is structured as follows: 

```
.
├── LICENSE.txt
├── README.md
├── setup.py
├── conda_requirements.txt
├── create_conda_env.bat
├── add_env_pip_packages.bat
├── config
├── functions
│   ├── crop
│   ├── find_artefacts
│   ├── loading_TMSi
│   ├── main_resync
│   ├── plotting
│   ├── preprocessing
│   ├── tmsi_poly5reader
│   └── utils
├── notebook
│   └── ReSync.ipynb

```

```notebook``` contains the jupyter notebook to run resync functions. ```main_resync``` contains the two main functions used for the analysis: ```run_resync``` and ```run_timeshift_analysis```.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine. 

### Repository
* GUI: use a git-manager of preference, and clone: https://github.com/juliettevivien/ReSync.git
* Command line:
    - set working directory to desired folder and run: ```git clone https://github.com/juliettevivien/ReSync.git```
    - to check initiated remote-repo link, and current branch: ```cd ReSync```, ```git init```, ```git remote -v```, ```git branch``` (switch to branch main e.g. with git checkout main)

### Environment
* GUI: Create a python environment with the correct requirements. Either use the GUI of a environments-manager (such as anaconda), and install all dependencies mentioned in the setup.py.
* Command line: you can easily install the required environment from your command line prompt. Note: since some packages are only available via ```pip install```, the environment-installation requires 2 commands: one for ```conda install```, and one for ```pip install```. Steps to perform in your (anaconda) prompt:
    - navigate to repo directory, e.g.: ```cd Users/USERNAME/Research/ReSync```
    - create environment using batch install: ```.\create_conda_env.bat``` (confirm Proceed? with ```y```)
    - install additional packages to environment (required for pip install packages): ```.\add_env_pip_packages.bat```
    - activate conda environment with: ```conda activate resync```

## User Instructions:

* Make sure your environment has the required packages installed, either manually, or by following the instructions above.
* ReSync can be executed directly from the notebook: ```notebook/ReSync.ipynb```.

## Authors

* **Juliette Vivien** - *Initial work* - 

Contributor: https://github.com/jgvhabets

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

