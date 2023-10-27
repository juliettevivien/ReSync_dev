"""
utilisation function
"""

import os
import json
from tkinter.filedialog import askdirectory
import scipy
import numpy as np
import operator


def _define_folders():

    """
    This function is used if the user hasn't already define 
    the saving path in the config.json file (back up function).
    """

    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    saving_folder = askdirectory(title= 'Select Saving Folder') 
    saving_path = os.path.join(saving_folder, loaded_dict['subject_ID'])
    if not os.path.isdir(saving_path):
        os.makedirs(saving_path)

    return saving_path



### FUNCTIONS FOR CONVERSION time/index ###

# Conversion between index and timestamps

def _convert_index_to_time(
    art_idx: list,
    sf: int
):
    """ 
    Function to calculate timestamps 
    of indexes from a list
    
    Inputs:
        - art_idx : list of indexes
        - sf : sampling frequency of the signal 
        from which the indexes come from

    Returns:
        - art_time : list of timestamps
    """

    art_time = []
    for n in np.arange(0, len(art_idx), 1):
        art_time_x = art_idx[n]/sf
        art_time.append(art_time_x)
        
    return art_time



def _convert_time_to_index(
    art_time: list, 
    sf: int
):
    
    """ 
    Function to calculate indexes from a list of timestamps.
    
    Inputs:
        - art_time : list of timestamps
        - sf : sampling frequency of the signal 
        from which the timestamps come from
    
    Returns:
        - art_idx : list of indexes    
    """

    art_idx = []
    for n in np.arange(0, len(art_time), 1):
        art_idx_x = art_time[n]*sf
        art_idx.append(art_idx_x)
    
    return art_idx




def _extract_elements(data_list, indices_to_extract):
    # Create an itemgetter object with the indices specified in indices_to_extract
    getter = operator.itemgetter(*indices_to_extract)

    # Use the itemgetter to extract the elements from the data_list
    extracted_elements = getter(data_list)

    return extracted_elements



def _get_input_y_n(message: str) -> str:

    """Get `y` or `n` user input."""

    while True:

        user_input = input(f"{message} (y/n)? ")

        if user_input.lower() in ["y", "n"]:

            break

        print(

            f"Input must be `y` or `n`. Got: {user_input}."

            " Please provide a valid input."

        )

    return user_input


def _filtering(
        BIP_channel
):
    """
    This function applies a highpass filter at 1Hz to detrend the data.
    """

    b, a = scipy.signal.butter(1, 0.05, 'highpass')
    filteredHighPass = scipy.signal.filtfilt(b, a, BIP_channel)

    return filteredHighPass
