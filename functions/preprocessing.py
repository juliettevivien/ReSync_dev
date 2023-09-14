import numpy as np
import functions.preprocessing as preproc
import scipy

# Function to pre-process BIP channel 

def filtering(
        BIP_channel
):
    """
    This function applies a highpass filter at 1Hz to detrend the data.
    """

    b, a = scipy.signal.butter(1, 0.05, 'highpass')
    filteredHighPass = scipy.signal.filtfilt(b, a, BIP_channel)

    return filteredHighPass
