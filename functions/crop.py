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
    real_index_LFP: list
):

    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)


    # LFP #
    # Crop beginning of LFP recording 1 second before first artefact:

    time_start_LFP_0 = art_time_LFP[0]-1 # 1s before first artefact
    index_start_LFP_0 = time_start_LFP_0*(loaded_dict['sf_LFP'])
    index_start_LFP = index_start_LFP_0 + real_index_LFP ## adjust index for proper alignement

    LFP_df = pd.DataFrame(LFP_array) # convert np.ndarray to dataframe
    LFP_df_transposed = pd.DataFrame.transpose(LFP_df) # invert rows and columns

    LFP_df_offset = LFP_df_transposed.truncate(before=index_start_LFP) # remove all rows before first artefact
    LFP_df_offset = LFP_df_offset.reset_index(drop=True) # reset indexes


    ## TMSi ##
    # Crop beginning of external recordings 1s before first artefact:

    # find the index of the row corresponding to 1 second before first artefact
    time_start_external = (art_time_BIP[0])-1
    index_start_external = time_start_external*loaded_dict['sf_external']

    external_array = external_file
    external_df = pd.DataFrame(external_array) # convert np.ndarray to dataframe
    external_df_transposed = pd.DataFrame.transpose(external_df) # invert rows and columns

    external_df_offset = external_df_transposed.truncate(before=index_start_external) # remove all rows before first artefact
    external_df_offset = external_df_offset.reset_index(drop=True) # reset indexes

    #### Check which recording is the longest, and crop it to give it the same duration as the other one:
    LFP_rec_duration = len(LFP_df_offset)/loaded_dict['sf_LFP']
    external_rec_duration = len(external_df_offset)/loaded_dict['sf_external']

    if LFP_rec_duration > external_rec_duration:
        rec_duration = external_rec_duration
        index_stop_LFP = rec_duration*loaded_dict['sf_LFP']
        LFP_df_offset2 = LFP_df_offset.truncate(after=index_stop_LFP-1)
        external_df_offset2 = external_df_offset
    elif external_rec_duration > LFP_rec_duration:
        rec_duration = LFP_rec_duration
        index_stop_external = rec_duration*loaded_dict['sf_external']
        external_df_offset2 = external_df_offset.truncate(after=index_stop_external-1)
        LFP_df_offset2 = LFP_df_offset


    # rename properly columns in both cropped recordings:
    LFP_df_offset2.columns = LFP_rec_ch_names
    LFP_df_offset2 = LFP_df_offset2.reset_index(drop=True)
    external_df_offset2.columns = external_rec_ch_names
    external_df_offset2 = external_df_offset2.reset_index(drop=True)

    

    return LFP_df_offset2, external_df_offset2