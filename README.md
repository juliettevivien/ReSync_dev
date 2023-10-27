# ReSync

## About
ReSync is an open-acess tool to align intracerebral recordings (from DBS electrodes) with external electrophysiological recordings. A manuscript describing ReSync's functionality and methodology will (hopefully) follow.

This repo is structured as follows: 

```
.
├── LICENSE.txt
├── README.md
├── setup.py
├── env_requirements.txt
├── config
│   └── config.json
├── functions
│   ├── crop.py
│   ├── find_artefacts.py
│   ├── find_packet_loss.py
│   ├── interactive.py
│   ├── loading_TMSi.py
│   ├── main_resync.py
│   ├── plotting.py.py.py
│   ├── preprocessing
│   ├── tmsi_poly5reader
│   └── utils.py
└── notebook
    └── ReSync.ipynb

```
```env_requirements``` contains all the packages and their version needed to run the ReSync algorithm.
```notebook``` contains the jupyter notebook to run resync functions. ```main_resync``` contains the main functions used for the analysis: ```run_resync``` and ```check_packet_loss```.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine. 

#### Repository
* GUI: use a git-manager of preference, and clone: https://github.com/juliettevivien/ReSync.git
* Command line:
    - set working directory to desired folder and run: ```git clone https://github.com/juliettevivien/ReSync.git```
    - to check initiated remote-repo link, and current branch: ```cd ReSync```, ```git init```, ```git remote -v```, ```git branch``` (switch to branch main e.g. with git checkout main)

#### Environment
* GUI: Create a python environment with the correct requirements. Either use the GUI of a environments-manager (such as anaconda), and install all dependencies mentioned in the env_requirements.txt.
* Anaconda prompt: you can easily install the required environment from your Anaconda prompt:
    - navigate to repo directory, e.g.: ```cd Users/USERNAME/Research/ReSync```
    - ```conda create --name resync python==3.10.9 pandas==1.5.3 scipy==1.10.0 numpy==1.23.5 matplotlib==3.6.3 openpyxl==3.0.10 jupyter==1.0.0``` (Confirm Proceed? with ```y```)
    - ```conda activate resync```
    - ```pip install mne==1.3.0 pymatreader```


## User Instructions:

* Make sure your environment has the required packages installed, either manually, or by following the instructions above.
* ReSync can be executed directly from the notebook: ```notebook/ReSync.ipynb```.

#### 1. Fill in the config.json document:
```
{
    "saving_path": "....", # the path to save the cropped recordings and all the figures 
    "subject_ID": "...", # the ID of the subject/session
    "ch_name_BIP": "BIP 01", # the name of the channel containing the artefacts in the external recorder (bipolar channel)
    "kernel": "2", # the kernel to use for artefact detection in intracerebral channel (either "1" or "2"). Best choice is usually "2".
    "LFP_ch_index": 0, # the index of the channel containing the artefacts in the intracerebral recorder
    "BIP_ch_index": 0, # AUTOMATICALLY FILLED the index of the channel containing the artefacts in the external recorder (bipolar channel)
    "thresh_external": false,  # leave to false if the artefacts in the external recording are properly detected, but insert a value if artefacts are not well detected (this value depends on the sampling frequency of the external data recorder, our default threshold is set to -0.001)
    "consider_first_seconds_LFP": null, # change this delay (in seconds) if the session was in StimOn, it will only look for artefacts during the X first seconds and X last seconds of the recording
    "consider_first_seconds_external": null, # change this delay (in seconds) if the session was in StimOn, it will only look for artefacts during the X first seconds and X last seconds of the recording 
    "ignore_first_seconds_external": null, # change this delay (in seconds) if you have unrelated artefacts in your external channel in the beginning of the recording
```

#### 2. Open the notebook and import your own data
* run the first cells to import the librairies, define the project_path and import the functions
* load you own intracerebral data. To run, the ```run_resync``` function will need:
    - LFP_array (np.ndarray, 6d): the raw LFP recording, containing all channels
    - lfp_sig (np.ndarray, 1d): the channel containing the LFP signal from the hemisphere where the stimulation was delivered to generate artefacts
    - LFP_rec_ch_names (list): names of all the channels, in a list (will be used to annotate cropped recording)
    - sf_LFP (int): sampling frequency of intracerebral signal
* load your own external data. To run, the ```run_resync``` function will need:
    - BIP_channel (np.ndarray, 1d): the channel containing the signal from the bipolar electrode used to pick up the artefacts on the IPG/cable
    - external_file (np.ndarray, multi-dimensional): the raw external recording containing all recorded channels
    - external_rec_ch_names (list, same length as the number of channels in external_file): list of the channels names, to rename them accordingly after alignment
    - sf_external (int): sampling frequency of the external data recorder

#### 3. Use run_resync
* run the cell with the ```run_resync``` function.
* If not convinced with sample automatically chosen in the intracranial recording:
     - try with other kernel
     - run the next cell (with ```interact.select_sample``` function) to manually select the proper sample and re-run
* when the recordings are properly aligned, the next cells can also be ran to analyze timeshift

#### 4. OPTIONAL Check timeshift
* run the cells from the notebook in the proper order. Interactive windows will appear for the selection of the last artefact in each recording modality:
    - manual selection of sample corresponding to last artefact start in intracerebral channel
    - manual selection of sample corresponding to last artefact start in external channel
* timeshift is then calculated
* the last artefact is plotted in both recordings aligned, with samples manually chosen indicated by a grey line

#### 5. OPTIONAL Check for packet loss in intracranial recording

## Authors

* **Juliette Vivien** - *Initial work* -

* **Jeroen Habets** - *Contributor* - https://github.com/jgvhabets

## Questions or contributions
Please don't hesitate to reach out if any questions or suggestions! @ juliette.vivien@charite.de  or https://twitter.com/vivien_juliette


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

