# import librairies
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import json

#import custom-made functions
import functions.utils as utils
import functions.find_artefacts as artefact
import functions.plotting as plot
import functions.crop as crop
import functions.preprocessing as preproc

## set font sizes and other parameters for the figures
SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=SMALL_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def run_resync(
    LFP_array, 
    lfp_sig, 
    LFP_rec_ch_names, 
    external_file,
    BIP_channel, 
    external_rec_ch_names,
    SHOW_FIGURES = True,
):

    """
    This function aligns the intracerebral recording with
    the external recording of the same session.

    Inputs:
        - LFP_array: the intracerebral recording containing 
            all recorded channels
        - lfp_sig: the channel of the intracerebral recording
            to be used for alignment (the one containing deep 
            brain stimulation artefacts)
        - LFP_rec_ch_names: the names of all the channels 
            recorded intracerebrally
        - external_file: the external recording containing 
            all recorded channels
        - BIP_channel: the channel of the external recording
            to be used for alignment (the one containing deep 
            brain stimulation artefacts, usually the channel 
            recorded with the bipolar electrode)
        - external_rec_ch_names: the names of all the channels 
            recorded externally
        - SHOW_FIGURES: True or False, depending of whether the user
        wants the figures to appear in the notebook directly or not.
    
    Outputs:
        - LFP_df_offset: the intracerebral recording containing 
            all recorded channels, cropped one second before the 
            first artefact
        - external_df_offset: the external recording containing 
            all recorded channels, cropped one second before the 
            first artefact
        The longest one of these two recordings is also cropped
        at the end, so that both of them have the exact same duration.
    
    """

    # import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    # set saving path
    if loaded_dict['saving_path'] == False:
        saving_path = utils.define_folders()
    else:
        saving_path = os.path.join(os.path.normpath(loaded_dict['saving_path']), loaded_dict['subject_ID'])
        if not os.path.isdir(saving_path):
            os.makedirs(saving_path)

    ### DETECT ARTEFACTS ###

    # find artefacts in intracerebral channel
    art_idx_LFP = artefact.find_LFP_sync_artefact(
        lfp_sig,
        use_kernel=loaded_dict['kernel'], 
        consider_first_seconds_LFP=loaded_dict['consider_first_seconds_LFP']
    )

    art_time_LFP = utils.convert_index_to_time(art_idx_LFP,
                                               loaded_dict['sf_LFP']) 

    # find artefacts in external bipolar channel
    filtered_external = preproc.filtering(BIP_channel) # preprocessing of external bipolar channel

    art_idx_BIP = artefact.find_external_sync_artefact(data= filtered_external, 
                                                       ignore_first_seconds_external=loaded_dict['ignore_first_seconds_external'], 
                                                       consider_first_seconds_external=loaded_dict['consider_first_seconds_external'])
    art_time_BIP = utils.convert_index_to_time(art_idx_BIP, 
                                               loaded_dict['sf_external'])

    # crop intracerebral and external recordings 1 second before first artefact
    (LFP_df_offset, 
     external_df_offset) = crop.crop_rec(LFP_array, 
                                         external_file, 
                                         art_time_LFP, 
                                         art_time_BIP, 
                                         LFP_rec_ch_names, 
                                         external_rec_ch_names, 
                                         loaded_dict['real_index_LFP'])

    ###  SAVE CROPPED RECORDINGS ###
    #Save LFP:
    LFP_df_offset.to_csv(saving_path + '\\Intracerebral_LFP_' + loaded_dict['subject_ID'] + '_' + str(loaded_dict['sf_LFP']) + 'Hz.csv', index=False) 

    #Save TMSi:
    external_df_offset.to_csv(saving_path + '\\External_data_' + loaded_dict['subject_ID'] + '_' + str(loaded_dict['sf_external']) + 'Hz.csv', index=False)
    

    ### PLOTS ###

    # Generate timescales:
    LFP_timescale_s = np.arange(0,(len(lfp_sig)/loaded_dict['sf_LFP']),(1/loaded_dict['sf_LFP']))
    external_timescale_s = np.arange(0,(len(BIP_channel)/loaded_dict['sf_external']),(1/loaded_dict['sf_external']))

    # PLOT 1 : plot the signal of the channel used for artefact detection in intracerebral recording:
    plot.plot_LFP_artefact_channel(loaded_dict['subject_ID'], 
                                   LFP_timescale_s, 
                                   lfp_sig, 'darkorange', 
                                   savingpath = saving_path)
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    # PLOT 2 : plot the signal of the channel used for artefact detection in external recording:
    plot.plot_BIP_artefact_channel(loaded_dict['subject_ID'], 
                                   external_timescale_s, 
                                   BIP_channel,
                                   'darkcyan',
                                   savingpath = saving_path)
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    # PLOT 3 : plot the intracerebral channel with its artefacts detected:
    plot.plot_channel(loaded_dict['subject_ID'], 
                      LFP_timescale_s, 
                      lfp_sig,
                      'darkorange')
    plt.ylabel('Intracerebral LFP channel (µV)')
    for xline in art_time_LFP:
        plt.axvline(x=xline, 
                    ymin=min(lfp_sig), 
                    ymax=max(lfp_sig), 
                    color='black', 
                    linestyle='dashed',
                    alpha=.3,)
    plt.gcf()
    plt.savefig(saving_path + '\\Intracerebral channel with artefacts detected - kernel ' + str(loaded_dict['kernel']) + '.png',bbox_inches='tight')
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    # PLOT 4 : plot the first artefact detected in intracerebral channel for verification of sample choice:
    plot.plot_channel(loaded_dict['subject_ID'], 
                      LFP_timescale_s, 
                      lfp_sig, 'darkorange',
                      scatter=True)
    plt.ylabel('Intracerebral LFP channel (µV)')
    for xline in art_time_LFP:
        plt.axvline(x=xline, 
                    ymin=min(lfp_sig), 
                    ymax=max(lfp_sig), 
                    color='black', 
                    linestyle='dashed', 
                    alpha=.3,)
    plt.xlim(art_time_LFP[0]-0.1,art_time_LFP[0]+0.3)
    plt.gcf()
    plt.savefig(saving_path + '\\Intracerebral channel - first artefact detected - kernel ' + str(loaded_dict['kernel']) + '.png',bbox_inches='tight')
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    # PLOT 5 : plot the external channel with its artefacts detected:
    plot.plot_channel(loaded_dict['subject_ID'], 
                      external_timescale_s, 
                      BIP_channel, 
                      'darkcyan')
    plt.ylabel('Artefact channel BIP (mV)')
    for xline in art_time_BIP:
        plt.axvline(x=xline, 
                    color='black', 
                    linestyle='dashed', 
                    alpha=.3,)
    plt.gcf()
    plt.savefig(saving_path + '\\External bipolar channel with artefacts detected.png',bbox_inches='tight')
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    # PLOT 6 : plot the first artefact detected in external channel for verification of sample choice:
    plot.plot_channel(loaded_dict['subject_ID'], 
                      external_timescale_s, 
                      BIP_channel, 
                      'darkcyan',
                      scatter=True)
    plt.ylabel('Artefact channel BIP - Voltage (mV)')
    for xline in art_time_BIP:
        plt.axvline(x=xline, 
                    color='black', 
                    linestyle='dashed', 
                    alpha=.3,)
    plt.xlim(art_time_BIP[0]-0.015, art_time_BIP[0]+0.015)
    plt.gcf()
    plt.savefig(saving_path + '\\External bipolar channel - first artefact detected.png',bbox_inches='tight')   
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    return LFP_df_offset, external_df_offset



def run_timeshift_analysis(
        LFP_df_offset, 
        external_df_offset,
        SHOW_FIGURES = True
):
    
    """"
    This function looks for timeshift between the intracerebral
    recording and the external recording. It is useful to check 
    for potential difference in clocking systems between the two
    recorders, or to detect packet loss in intracerebral recordings.

    Inputs:
        - LFP_df_offset: the intracerebral recording containing 
            all recorded channels, cropped one second before the 
            first artefact (after processing with run_resync function)
        - external_df_offset: the external recording containing 
            all recorded channels, cropped one second before the 
            first artefact (after processing with run_resync function)
        - SHOW_FIGURES: True or False, depending of whether the user
        wants the figures to appear in the notebook directly or not.
    
    Output:
        - timeshift: the timeshift of the last detected artefact in
        aligned recordings
    """

    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    #set saving path
    if loaded_dict['saving_path'] == False:
        saving_path = utils.define_folders()
    else:
        saving_path = os.path.join(os.path.normpath(loaded_dict['saving_path']), loaded_dict['subject_ID'])
        if not os.path.isdir(saving_path):
            os.makedirs(saving_path)


    ### DETECT ARTEFACTS ###

    # Reselect artefact channels in the aligned (= cropped) files
    LFP_channel_offset = LFP_df_offset.iloc[:,loaded_dict['LFP_ch_index']].to_numpy()  
    BIP_channel_offset = external_df_offset.iloc[:,loaded_dict['BIP_ch_index']].to_numpy() 


    # find artefacts again in cropped intracerebral LFP channel:
    art_idx_LFP_offset = artefact.find_LFP_sync_artefact(lfp_data=LFP_channel_offset,
                                                         use_kernel=loaded_dict['kernel'],
                                                         consider_first_seconds_LFP=loaded_dict['consider_first_seconds_LFP']
    )

    art_time_LFP_offset = utils.convert_index_to_time(art_idx_LFP_offset,
                                                      loaded_dict['sf_LFP']
    )

    # pre-processing of external bipolar channel before searching artefacts:
    filtered_external_offset = preproc.filtering(BIP_channel_offset)

    # find artefacts again in cropped external bipolar channel:
    art_idx_BIP_offset = artefact.find_external_sync_artefact(data = filtered_external_offset, 
                                                              ignore_first_seconds_external=loaded_dict['timeshift_ignore_first_seconds_external'], 
                                                              consider_first_seconds_external=loaded_dict['consider_first_seconds_external']
    )
    art_time_BIP_offset = utils.convert_index_to_time(art_idx_BIP_offset, 
                                                      loaded_dict['sf_external']
    )


    ### SELECT CORRECT ARTEFACTS ###
    # the algorithm might detect "artefacts" that are not really artefacts. 
    # With the images saved, the user can select the ones that are correct 
    # and enter their index in the config.json file.
    real_art_time_LFP_offset= utils.extract_elements(art_time_LFP_offset,
                                                     loaded_dict['index_real_artefacts_LFP']
    ) 
    real_art_time_BIP_offset= utils.extract_elements(art_time_BIP_offset, 
                                                     loaded_dict['index_real_artefacts_BIP']
    )


    ### ASSESS TIMESHIFT ###

    # once the artefacts are all correctly selected, the timeshift can be computed:
    delay = []
    for i in (np.arange(0,len(real_art_time_LFP_offset))):
        delay.append(real_art_time_BIP_offset[i]-real_art_time_LFP_offset[i])
    delay_ms = []
    for i in (np.arange(0,len(delay))):
        delay_ms.append(delay[i]*1000)
    
    mean_diff = sum(delay_ms)/len(delay_ms)
    
    timeshift = delay_ms[-1]


    ## PLOTS ##

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(0,(len(LFP_channel_offset)/loaded_dict['sf_LFP']),1/loaded_dict['sf_LFP'])
    external_timescale_offset_s = np.arange(0,(len(BIP_channel_offset)/loaded_dict['sf_external']),1/loaded_dict['sf_external'])

    # PLOT 1: Both signals aligned with all their artefacts detected:
    fig, (ax1, ax2) = plt.subplots(2,1)
    fig.suptitle(str(loaded_dict['subject_ID']))
    fig.set_figheight(6)
    fig.set_figwidth(12)
    ax1.axes.xaxis.set_ticklabels([])
    ax2.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax2.set_ylabel('External bipolar channel (mV)')
    ax1.set_xlim(0,len(LFP_channel_offset)/loaded_dict['sf_LFP']) 
    ax2.set_xlim(0,len(LFP_channel_offset)/loaded_dict['sf_LFP']) 
    ax1.plot(LFP_timescale_offset_s,LFP_channel_offset,color='darkorange',zorder=1, linewidth=0.3)
    for xline in art_time_LFP_offset:
        ax1.axvline(x=xline, ymin=min(LFP_channel_offset), ymax=max(LFP_channel_offset),
                    color='black', linestyle='dashed', alpha=.3,)
    ax2.plot(external_timescale_offset_s,BIP_channel_offset, color='darkcyan',zorder=1, linewidth=0.1) 
    for xline in art_time_BIP_offset:
        ax2.axvline(x=xline, color='black', linestyle='dashed', alpha=.3,)

    fig.savefig(saving_path + '\\Intracerebral and external aligned channels with artefacts.png',bbox_inches='tight')
    if SHOW_FIGURES: plt.show()
    else: plt.close()


    # PLOT 2: All artefacts detected and their associated timeshift
    plt.figure(figsize=(30, 10))
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.2, wspace=0.5)
    plt.suptitle(str(loaded_dict['subject_ID']) + '\n\nThe mean difference is: ' +str(round(mean_diff,2))+ 'ms')
    # loop through the index to make new plots for each artefact:
    for n, m in zip(range(0,len(delay_ms),1),range(len(delay_ms),(len(delay_ms))*2,1)) :
        # add a new subplot iteratively
        ax1 = plt.subplot(2, len(delay_ms), n + 1)
        ax2 = plt.subplot(2, len(delay_ms), m + 1)
        ax1.axes.xaxis.set_ticklabels([])
        ax2.axes.xaxis.set_major_formatter('{:.2f}'.format)
        ax2.set_xlabel('Time (s)')
        ax1.set_ylabel('Intracerebral LFP channel (µV)')
        ax2.set_ylabel('External bipolar channel (mV)')
        ax1.set_title('artefact ' + str((loaded_dict['index_real_artefacts_LFP'][n])+1))
        ax1.set_xlim((real_art_time_LFP_offset[n]-0.050),(real_art_time_LFP_offset[n]+0.1))
        ax2.set_xlim((real_art_time_LFP_offset[n]-0.050),(real_art_time_LFP_offset[n]+0.1))
        ax1.plot(LFP_timescale_offset_s,LFP_channel_offset,color='peachpuff',zorder=1)
        ax1.scatter(LFP_timescale_offset_s,LFP_channel_offset,color='darkorange',s=4,zorder=2) 
        ax1.scatter(LFP_timescale_offset_s,LFP_channel_offset,color='darkorange',s=4,zorder=2) 
        for xline in real_art_time_LFP_offset:
            ax1.axvline(x=xline, ymin=min(LFP_channel_offset), ymax=max(LFP_channel_offset),
                color='black', linestyle='dashed', alpha=.3,)
        ax2.plot(external_timescale_offset_s,BIP_channel_offset, color='paleturquoise',zorder=1) 
        ax2.scatter(external_timescale_offset_s,BIP_channel_offset, color='darkcyan',s=4,zorder=2)
        for xline in real_art_time_BIP_offset:
            ax2.axvline(x=xline, color='black', linestyle='dashed', alpha=.3,)


        ax1.text(0.05,0.85,s='delay intra/exter: ' +str(round(delay_ms[n],2))+ 'ms',fontsize=14,transform=ax1.transAxes)

    plt.gcf()
    plt.savefig(saving_path + '\\Intracerebral and external aligned channels - timeshift all artefacts.png',bbox_inches='tight')
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    return timeshift