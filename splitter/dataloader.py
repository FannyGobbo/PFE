import os
from os.path import isfile

import torch
from torch import from_numpy
import torch.nn.functional as F

import librosa
import numpy as np

import pickle

d_model = 16000

# Pre-processing
def preprocess_audio(file_path):
	# Load audio
	y, sr = librosa.load(file_path)
	
	# Check sampling rate
	if sr != 22050:
		print(f"Error sampling rate != 22,050 Hz: {sr} Hz")

	# Spectrogram computation
	spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)

	# Normalize frequencies
	spectrogram = librosa.power_to_db(spectrogram, ref=np.max)
	
	# Normalize input
	input_tensor = from_numpy(spectrogram).unsqueeze(0)
	print(input_tensor.shape[2], y.shape)
	input_tensor = F.pad(input_tensor, (0, 16000-input_tensor.size()[2]))

	return from_numpy(y).unsqueeze(0), input_tensor
	
def save_data (data, path):
	with open(path, "wb") as fp:
		pickle.dump(data, fp)

def load_data (path):
	with open(path, "rb") as fp:
		return pickle.load(fp)

def scan_and_process (path, subset):
	xt_train: List[torch.Tensor] = []
	yt_train: List[torch.Tensor] = []
	xt_test: List[torch.Tensor] = []
	yt_test: List[torch.Tensor] = []
	
	xf_train: List[torch.Tensor] = []
	yf_train: List[torch.Tensor] = []
	xf_test: List[torch.Tensor] = []
	yf_test: List[torch.Tensor] = []
	
	for i, node in enumerate(os.scandir(path)):
		if i == 10 and subset:
			break
		
		print(i)
		
		if not isfile(node):
			
			for n in os.scandir(node):
				if isfile(n):
					(t, f) = preprocess_audio(n.path)
					xt_train.append(t)
					xf_train.append(f)
			
			for n in os.scandir(node.path.replace("Mixtures", "Sources")):
				if isfile(n):
					(t, f) = preprocess_audio(n.path)
					yt_train.append(t)
					yf_train.append(f)
			
	for i, node in enumerate(os.scandir(path.replace("Dev", "Test"))):
		if i == 10 and subset:
			break
		
		print(i)
		
		if not isfile(node):
			
			for n in os.scandir(node.path):
				if isfile(n):
					(t, f) = preprocess_audio(n.path)
					xt_test.append(t)
					xf_test.append(f)
			
			for n in os.scandir(node.path.replace("Mixtures", "Sources")):
				if isfile(n):
					(t, f) = preprocess_audio(n.path)
					yt_test.append(t)
					yf_test.append(f)
						
	return xt_train, yt_train, xt_test, yt_test, xf_train, yf_train, xf_test, yf_test

def get_spec_waveform (train_mixtures_path, x_train_path, y_train_path, x_test_path, y_test_path, subset):
	xt_train, yt_train, xt_test, yt_test, xf_train, yf_train, xf_test, yf_test = scan_and_process(train_mixtures_path, subset)
	
	xf_train = [x for x in xf_train] # 1, 128, 16000 (batch, midi, bins)
	xf_test = [x for x in xf_test]
	yf_train = [torch.cat([yf_train[i], yf_train[i+1], yf_train[i+2], yf_train[i+3]], dim=2) for i in range(0, len(yf_train), 4)]
	yf_test = [torch.cat([yf_test[i], yf_test[i+1], yf_test[i+2], yf_test[i+3]], dim=2) for i in range(0, len(yf_test), 4)]
	
	# Join together the raw waveform and the spectrogram
	x_train = (xt_train, xf_train)
	y_train = (yt_train, yf_train)
	x_test = (xt_test, xf_test)
	y_test = (yt_test, yf_test)
	
	save_data(x_train, x_train_path)
	save_data(y_train, y_train_path)
	save_data(x_test, x_test_path)
	save_data(y_test, y_test_path)
	
	return x_train, y_train, x_test, y_test

def get_dataset (subset=False):
	train_mixtures_path = "../../data/DSD100/Mixtures/Dev"
	if not subset:
		x_train_path = "x_train.pkl"
		y_train_path = "y_train.pkl"
		x_test_path = "x_test.pkl"
		y_test_path = "y_test.pkl"
	else:
		x_train_path = "x_train_d.pkl"
		y_train_path = "y_train_d.pkl"
		x_test_path = "x_test_d.pkl"
		y_test_path = "y_test_d.pkl"

	# If data is already saved
	if (isfile(x_train_path) and isfile(y_train_path) and isfile(x_test_path) and isfile(y_test_path)):
		x_train = load_data(x_train_path)
		y_train = load_data(y_test_path)
		x_test = load_data(x_test_path)
		y_test = load_data(y_test_path)
		
	# Else process and save audio files
	else:
		x_train, y_train, x_test, y_test = get_spec_waveform(train_mixtures_path, x_train_path, y_train_path, x_test_path, y_test_path, subset)
	
	return x_train, y_train, x_test, y_test

#x_train, y_train, x_test, y_test = get_dataset()
#print(len(xf_train), len(yf_train), len(xf_test), len(yf_test), xf_train[0].size(), len(yf_train[0]))

# To be used in training.py
def save_as_wav (id, y: list[torch.Tensor], is_mel=True):
	filenames=["bass.wav", "drums.wav", "vocals.wav", "other.wav"]
	path=f"results/{id}/splitted-sources/"
	
	if is_mel:
		y = librosa.feature.mel_to_audio(y=y, sr=22050)
	
	split_y = torch.split(y, 4)
	for i, f in enumerate(filenames):
		librosa.output.write_file(path=path+f, y=y[i], sr=22050)
		
		
		
		
		
		
		
		
		
		
