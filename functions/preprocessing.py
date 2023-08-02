import numpy as np
import functions.preprocessing as preproc
import scipy

# Function to pre-process BIP channel 

def cleaning_function(
    signal_before: np.ndarray
):
    
    """ 
    Function that removes "clipping" artefacts, 
    i.e. saturation of amplifier due to cable strain. 
    It calculates the mean of the signal and replaces 
    every higher value by the mean. This function can
    only be used if the stim artefact has a specific 
    polarity (i.e. stim artefact goes downward/clipping
    goes upward).

    Inputs:
        - timescale: single channel array containing timestamps
        - signal_before: single channel array containing stim artefacts

    Returns:
        - signal_after: signal without clipping, as a single channel array
    """

    mean = np.mean(signal_before)
    range1 = np.arange(0,len(signal_before)-1,1)
    signal_after = signal_before.copy()

    for n in range1:
        if signal_after[n]> mean:
            signal_after[n] = mean
        else:
            n = n+1
      
    return signal_after


def filtering(
        BIP_channel
):
    BIP_channel_copy = preproc.cleaning_function(BIP_channel)
    b, a = scipy.signal.butter(1, 0.05, 'highpass')
    filteredHighPass = scipy.signal.filtfilt(b, a, BIP_channel_copy)

    return filteredHighPass
