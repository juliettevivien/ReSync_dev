import numpy as np
from scipy.signal import find_peaks
from itertools import compress
import os
import json


# Detection of artefacts in TMSi

def find_external_sync_artefact(
    data: np.ndarray, 
    ignore_first_seconds_external=None, 
    consider_first_seconds_external=None
):

    """ 
    Function that finds artefacts caused by
    augmenting-reducing stimulation from 0 to 1mA without ramp.
    For correct functioning, the external data recording should
    start in stim-off, and typically short pulses
    are given (without ramping). 
    This function uses a fixed threshold, which will work
    properly if the amplitude of the stimulation delivered
    is not below 1mA. 
    The signal must be pre-processed previously with a high-pass 
    Butterworth filter (1Hz) to ensure removal of slow drifts
    and offset around 0. Otherwise, the threshold will not
    allow for a proper detection of stim artefacts (cf lp.cleaning_function)

    Inputs:
        - data : single channel as np.ndarray
        - ignore_first_seconds_external : if given, the first n-seconds
        will be ignored (back-up, in case recording was
        started with stim ON, or if there are huge artefacts in the beginning)
        - consider_first_seconds_external : if given, only artefacts in
        the first (and last) n-seconds are considered (in case the
        recording is StimON, it ignores the other amplitude changes)
    
    Returns:
        - index_artefact_start_external : a list with all stim-artefact starts. 
        This can also contain stim-artefacts not happening at the
        beginning or end of the recording. These have to be selected
        by the user afterwards (use item_getter function).

    """


    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    #initialize variables (lists and state)
    index_artefact_start_external = []
    index_artefact_stop_external = []
    value_artefact_start_external =[]
    value_artefact_stop_external = []
    stimON = False

    if loaded_dict['thresh_external'] == False:
        thresh_BIP = -0.001
    else:
        thresh_BIP = loaded_dict['thresh_external']

    start_time = 0
    stop_time = len(data)-2

    if ignore_first_seconds_external:
        start_time = ignore_first_seconds_external*loaded_dict['sf_external']

    if consider_first_seconds_external:
        stop_time = consider_first_seconds_external*loaded_dict['sf_external']


    #start looking at each value one by one and append the timepoint to the list depending on the state and if thresh_BIP is crossed
    for q in range(start_time,stop_time):
        if (stimON == False) and (data[q] <= thresh_BIP) and (data[q] < data[q+1]) and (data[q] < data[q-1]):
            index_artefact_start_external.append(q)
            value_artefact_start_external.append(data[q])
            stimON = True
            q = q+1
        if (stimON == True) and (data[q] <= thresh_BIP) and (data[q] < data[q+1]) and (data[q] < data[q-1]):
            if (all(data[(q+2):(q+3000)] > thresh_BIP)):
                index_artefact_stop_external.append(q)
                value_artefact_stop_external.append(data[q])
                stimON = False
                q = q+1
        else:
            q = q+1

    if consider_first_seconds_external:
        for q in range(len(data)-stop_time,len(data)-2):
            if (stimON == False) and (data[q] <= thresh_BIP) and (data[q] < data[q+1]) and (data[q] < data[q-1]):
                index_artefact_start_external.append(q)
                value_artefact_start_external.append(data[q])
                stimON = True
                q = q+1
            if (stimON == True) and (data[q] <= thresh_BIP) and (data[q] < data[q+1]) and (data[q] < data[q-1]):
                if (all(data[(q+2):(q+3000)] > thresh_BIP)):
                    index_artefact_stop_external.append(q)
                    value_artefact_stop_external.append(data[q])
                    stimON = False
                    q = q+1
            else:
                q = q+1

    return index_artefact_start_external





# Detection of artefacts in LFP

def find_LFP_sync_artefact(
    lfp_data: np.ndarray, 
    use_kernel: str = '1',
    consider_first_seconds_LFP=None,
):
    """
    Function that finds artefacts caused by
    augmenting-reducing stimulation from 0 to 1mA without ramp.
    For correct functioning, the LFP data should
    start in stim-off, and typically short pulses
    are given (without ramping).
    The function uses a kernel which mimics the stimulation-
    artefact. This kernel is multiplied with time-series
    snippets of the same length. If the time-serie is
    similar to the kernel, the dot-product is high, and this
    indicates a stim-artefact.

    Input:
        - lfp_data: single channel as np.ndarray (the function
            automatically inverts the signal if first a positive
            peak is found, this indicates an inverted signal)
        - use_kernel: decides whether kernel 1 or 2 is used,
            kernel 1 is straight-forward and finds a steep decrease,
            kernel 2 mimics the steep decrease and slow
            recovery of the signal. default is kernel 1.
        - consider_first_seconds_LFP: if given, only artefacts in the first
            (and last) n-seconds are considered
    
    Returns:
        - list of idx: a list with all stim-artefact starts. This
            also contains stim-artefacts not happening at the
            beginning or end of the recording. These have to be
            selected by the user afterwards (item.getter function).
    """
    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    
    signal_inverted = False  # defaults false

    # checks correct input for use_kernel variable
    assert use_kernel in ['1', '2'], 'use_kernel incorrect'

    # kernel 1 only searches for the steep decrease
    # kernel 2 is more custom and takes into account the steep decrease and slow recover
    kernels = {'1': np.array([1, -1]),
               '2': np.array([1, 0, -1] + list(np.linspace(-1, 0, 20)))}
    ker = kernels[use_kernel]
    
    # get dot-products between kernel and time-serie snippets
    res = []  # store results of dot-products
    for i in np.arange(0, len(lfp_data) - len(ker)):
        res.append(ker @ lfp_data[i:i+len(ker)])  # calculate dot-product of vectors
        # the dot-product result is high when the timeseries snippet
        # is very similar to the kernel
    res = np.array(res)  # convert list to array

    # # normalise dot product results
    res = res / max(res)

    # calculate a ratio between std dev and maximum during
    # the first seconds to check whether an stim-artef was present 
    ratio_max_sd = np.max(res[:loaded_dict['sf_LFP']*30] / np.std(res[:loaded_dict['sf_LFP']*5]))
    
    # use peak of kernel dot products    
    pos_idx = find_peaks(x=res, height=.3 * max(res),
                        distance=loaded_dict['sf_LFP'])[0]
    neg_idx = find_peaks(x=-res, height=-.3 * min(res),
                        distance=loaded_dict['sf_LFP'])[0]

    # check whether signal is inverted
    if neg_idx[0] < pos_idx[0]:
        # the first peak should be POSITIVE (this is for the dot-product results)
        # actual signal is first peak negative
        # if NEG peak before POS then signal is inverted
        print('signal is inverted')
        signal_inverted = True
        #print(pos_idx[0], neg_idx[0])
        # re-check inverted for difficult cases with small pos-lfp peak before negative stim-artefact
        if (pos_idx[0] - neg_idx[0]) < 50:  # if first positive and negative are very close
            width_pos = 0
            r_i = pos_idx[0]
            while res[r_i] > (max(res) * .3):
                r_i += 1
                width_pos += 1
            width_neg = 0
            r_i = neg_idx[0]
            while res[r_i] < (min(res) * .3):
                r_i += 1
                width_neg += 1
            # undo invertion if negative dot-product (pos lfp peak) is very narrow
            if width_pos > (2 * width_neg):
                signal_inverted = False
                print('invertion undone')
            
           
    # return either POS or NEG peak-indices based on normal or inverted signal
    if not signal_inverted:
        stim_idx = pos_idx  # this is for 'normal' signal

    elif signal_inverted:
        stim_idx = neg_idx

    

    # check warn if NO STIM artefacts are suspected
    if len(stim_idx) > 20 and ratio_max_sd < 8:
        print('WARNING: probably the LFP signal did NOT'
              ' contain any artefacts. Many incorrect timings'
              ' could be returned')


    if consider_first_seconds_LFP:
        border_start = loaded_dict['sf_LFP']*consider_first_seconds_LFP
        border_end = len(lfp_data) - (loaded_dict['sf_LFP'] * consider_first_seconds_LFP)
        sel = np.logical_or(np.array(stim_idx) < border_start,
                             np.array(stim_idx) > border_end)
        stim_idx = list(compress(stim_idx, sel))


    # filter out inconsistencies in peak heights (assuming sync-stim-artefacts are stable)
    abs_heights = [max(abs(lfp_data[i-5:i+5])) for i in stim_idx]
    diff_median = np.array([abs(p - np.median(abs_heights)) for p in abs_heights])
    sel_idx = diff_median < (np.median(abs_heights) * .66)
    stim_idx = list(compress(stim_idx, sel_idx))
    # check polarity of peak
    if not signal_inverted:
        sel_idx = np.array([min(lfp_data[i-5:i+5]) for i in stim_idx]) < (np.median(abs_heights) * -.5)
    elif signal_inverted:
        sel_idx = np.array([max(lfp_data[i-5:i+5]) for i in stim_idx])  > (np.median(abs_heights) * .5)
    stim_idx = list(compress(stim_idx, sel_idx))


    return stim_idx
