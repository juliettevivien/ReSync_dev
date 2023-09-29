import pandas as pd    
import numpy as np
import os
import json  

def crop_rec(
    LFP_array: np.ndarray,
    external_file: np.ndarray,
    art_time_LFP,
    art_time_BIP,
    LFP_rec_ch_names: list,
    external_rec_ch_names: list,
    real_art_time_LFP: float,
    sf_LFP,
    sf_external
):

    """
    This function is used to crop the external recording and the
    intracerebral recording one second before the first artefact
    detected. The end of the longest one of those two recordings
    is also cropped, to have the same duration for the two recordings.
    The two cropped recordings are saved as .csv files.

    Inputs:
        - LFP_array: the intracerebral recording with all its recorded channels
        - external_file: the external recording with all its recorded channels
        - art_time_LFP: the timepoint when the artefact starts in the intracerebral 
        recording (found previously using the function find_LFP_sync_artefact)
        - art_time_BIP: the timepoint when the artefact starts in the external 
        recording (found previously using the function find_external_sync_artefact)
        - LFP_rec_ch_names: the names of all intracerebrally recorded channels 
        (to rename the cropped recording accordingly)
        - external_rec_ch_names: the names of all externally recorded channels 
        (to rename the cropped recording accordingly)
        - real_index_LFP: in case automatic detection was not 100% accurate, the 
        timepoint of the artefact "start" can be manually adjusted


    Returns:
        - LFP_df_offset2: the cropped intracerebral recording with all its recorded channels
        - external_df_offset2: the cropped external recording with all its recorded channels

    """


    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)


    # LFP #
    # Crop beginning of LFP recording 1 second before first artefact:
    if real_art_time_LFP == 0:
        time_start_LFP_0 = art_time_LFP[0]-1 # 1s before first artefact
        index_start_LFP = time_start_LFP_0*(sf_LFP)
    elif real_art_time_LFP != 0:
        diff_art_time = real_art_time_LFP - art_time_LFP[0]
        diff_art_idx = diff_art_time*(sf_LFP)
        time_start_LFP_0 = art_time_LFP[0]-1 # 1s before first artefact
        index_start_LFP_0 = time_start_LFP_0*(sf_LFP)
        index_start_LFP = index_start_LFP_0 + diff_art_idx

    LFP_df = pd.DataFrame(LFP_array) # convert np.ndarray to dataframe
    LFP_df_transposed = pd.DataFrame.transpose(LFP_df) # invert rows and columns

    LFP_df_offset = LFP_df_transposed.truncate(before=index_start_LFP) # remove all rows before first artefact
    LFP_df_offset = LFP_df_offset.reset_index(drop=True) # reset indexes


    ## TMSi ##
    # Crop beginning of external recordings 1s before first artefact:

    # find the index of the row corresponding to 1 second before first artefact
    time_start_external = (art_time_BIP[0])-1
    index_start_external = time_start_external*sf_external

    external_array = external_file
    external_df = pd.DataFrame(external_array) # convert np.ndarray to dataframe
    external_df_transposed = pd.DataFrame.transpose(external_df) # invert rows and columns

    external_df_offset = external_df_transposed.truncate(before=index_start_external) # remove all rows before first artefact
    external_df_offset = external_df_offset.reset_index(drop=True) # reset indexes

    #### Check which recording is the longest, and crop it to give it the same duration as the other one:
    LFP_rec_duration = len(LFP_df_offset)/sf_LFP
    external_rec_duration = len(external_df_offset)/sf_external

    if LFP_rec_duration > external_rec_duration:
        rec_duration = external_rec_duration
        index_stop_LFP = rec_duration*sf_LFP
        LFP_df_offset2 = LFP_df_offset.truncate(after=index_stop_LFP-1)
        external_df_offset2 = external_df_offset
    elif external_rec_duration > LFP_rec_duration:
        rec_duration = LFP_rec_duration
        index_stop_external = rec_duration*sf_external
        external_df_offset2 = external_df_offset.truncate(after=index_stop_external-1)
        LFP_df_offset2 = LFP_df_offset


    # rename properly columns in both cropped recordings:
    LFP_df_offset2.columns = LFP_rec_ch_names
    LFP_df_offset2 = LFP_df_offset2.reset_index(drop=True)
    external_df_offset2.columns = external_rec_ch_names
    external_df_offset2 = external_df_offset2.reset_index(drop=True)

    

    return LFP_df_offset2, external_df_offset2