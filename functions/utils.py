"""
utilisation function
"""

import os
import json
from tkinter.filedialog import askdirectory



def define_folders():

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



### FUNCTIONS FOR CONVERSION time/index###

import numpy as np

# Conversion between index and timestamps

def convert_index_to_time(
    art_idx: list,
    sf: int,
    milliseconds = False
):
    """ 
    Function to calculate timestamps 
    of indexes from a list
    
    Inputs:
        - art_idx : list of indexes
        - sf : sampling frequency of the signal 
        from which the indexes come from
        - milliseconds : True/False, default is False
    
    Returns:
        - art_time : list of timestamps
    """

    art_time = []
    for n in np.arange(0,len(art_idx),1):
        if milliseconds :
            art_time_x = art_idx[n]*1000/sf
            art_time.append(art_time_x)
        else :
            art_time_x = art_idx[n]/sf
            art_time.append(art_time_x)
        
    
    return art_time



def convert_time_to_index(
    art_time: list, 
    sf: int,
    milliseconds = False
):
    
    """ 
    Function to calculate indexes from a list of timestamps.
    
    Inputs:
        - art_time : list of timestamps
        - sf : sampling frequency of the signal 
        from which the timestamps come from
        - milliseconds : True/False, default is False
            
    Returns:
        - art_idx : list of indexes    
    """

    art_idx = []
    for n in np.arange(0,len(art_time),1):
        if milliseconds:
            art_idx_x = art_time[n]*sf/1000
            art_idx.append(art_idx_x)
        else:
            art_idx_x = art_time[n]*sf
            art_idx.append(art_idx_x)
    
    return art_idx



import operator

def extract_elements(data_list, indices_to_extract):
    # Create an itemgetter object with the indices specified in indices_to_extract
    getter = operator.itemgetter(*indices_to_extract)

    # Use the itemgetter to extract the elements from the data_list
    extracted_elements = getter(data_list)

    return extracted_elements


def get_input_y_n(message: str) -> str:

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