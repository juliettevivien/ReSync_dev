import numpy as np
import os
import json

# Function to open TMSi data

def load_TMSi_artefact_channel(
    TMSi_data
):
    
	"""
	Function that takes a poly5 object and returns in an array 
	the channel which will be used for sync ("BIP 01" in our settings),
	and in another array the timescale in milliseconds of the TMSi recording.
    It also prints informations about the recording (duration, channels, sampling frequency,...)
	
	Input:
		- TMSi_data : TMSiFileFormats.file_readers.poly5reader.Poly5Reader

	Returns:
		- TMSi_channel : single channel as np.ndarray
        - TMSi_file : np.ndarray (will be used later to crop TMSi channels all at once)
	"""

	# import SETTINGS
	json_path = os.path.join(os.getcwd(), 'config')
	json_filename = 'config.json'  # dont forget json extension
	with open(os.path.join(json_path, json_filename), 'r') as f:
		loaded_dict =  json.load(f)

	# Conversion of .Poly5 to MNE raw array
	toMNE = True
	TMSi_rec = TMSi_data.read_data_MNE()
	external_rec_ch_names = TMSi_rec.ch_names
	n_chan = len(TMSi_rec.ch_names)
	time_duration_TMSi_s = (TMSi_rec.n_times/TMSi_rec.info['sfreq']).astype(float)

	if is_channel_in_list(external_rec_ch_names, loaded_dict['ch_name_BIP']):
		ch_t = TMSi_rec.ch_names.index(loaded_dict['ch_name_BIP'])
		TMSi_channel = TMSi_rec.get_data()[ch_t]
		loaded_dict['BIP_ch_index'] = ch_t

		# save dict as JSON, 'w' stands for write
		with open(os.path.join(json_path, json_filename), 'w') as f:
				json.dump(loaded_dict, f, indent=4)
		
		print(     
			f'The data object has:\n\t{TMSi_rec.n_times} time samples,'      
			f'\n\tand a sample frequency of {TMSi_rec.info["sfreq"]} Hz'      
			f'\n\twith a recording duration of {time_duration_TMSi_s} seconds.'      
			f'\n\t{n_chan} channels were labeled as \n{TMSi_rec.ch_names}.')
		
		print(f'the channel used to align datas is the channel named {TMSi_rec.ch_names[ch_t]} and has index {ch_t}')

		TMSi_file = TMSi_rec.get_data()

	else:
		raise ValueError(f'The channel does not exist in the list. Please choose a channel in the following list and write its name in the config file  {external_rec_ch_names}')


	return TMSi_channel, TMSi_file, external_rec_ch_names



def is_channel_in_list(channel_array, desired_channel_name):
    if desired_channel_name.lower() in (channel.lower() for channel in channel_array):
        return True
    else:
        return False