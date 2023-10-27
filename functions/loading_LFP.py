# extract variables from LFP recording:
def set_lfp_data(
        LFP_rec, 
        ch_i = 0
):
    LFP_array = LFP_rec.get_data()
    lfp_sig = LFP_rec.get_data()[ch_i]
    LFP_rec_ch_names = LFP_rec.ch_names
    sf_LFP = int(LFP_rec.info["sfreq"])

    n_chan = len(LFP_rec.ch_names)
    time_duration_LFP = (LFP_rec.n_times/LFP_rec.info['sfreq']).astype(float)
    print(     
        f'The data object has:\n\t{LFP_rec.n_times} time samples,'      
        f'\n\tand a sample frequency of {LFP_rec.info["sfreq"]} Hz'      
        f'\n\twith a recording duration of {time_duration_LFP} seconds.'      
        f'\n\t{n_chan} channels were labeled as \n{LFP_rec.ch_names}.'
    )
    print(
        f'The channel containing artefacts has index {ch_i} and is named {LFP_rec.ch_names[ch_i]}'
    )

    return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP
