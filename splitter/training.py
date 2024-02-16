import torch
import torch.nn as nn
import torch.nn.functional as F

from functools import partial
import numpy as np

#from my_model import *
from simple_model import *
import dataloader as dl

import accelerate # memory and cpu/gpu optimizer
import tqdm # loop accelerator

import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Run on device:", device)

def train(model, x, y, optimizer, scheduler, accelerator):
	xt, xf = x
	yt, yf = y

	losses = []
	for epoch in range(10):
		tmp_losses = []
		for i in range(0, len(xt)-4, 3):
			accelerator.free_memory()
			optimizer.zero_grad()
			
			input = (torch.cat(xt[i:i+5], dim=0).to(device), torch.cat(xf[i:i+5], dim=0).to(device))
			target = (torch.cat(yt[i+1:i+4], dim=0).to(device), torch.cat(yf[i+1:i+4], dim=0).to(device))
			output = model(input)
			
			_, loss, _ = model.choose_spec_wave(output, target)
			tmp_losses.append(loss.item())

			accelerator.backward(loss)
			nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
			optimizer.step()
			scheduler.step()
		
		if len(tmp_losses) != 0:
			losses.append(sum(tmp_losses) / len(tmp_losses))
		
		#if epoch % 10 == 0:
		print(f"epoch {epoch+1} : {sum(losses) / (len(losses) if len(losses) != 0 else 1)}")

		if epoch % 100 == 0:
			save(model)
		
	return losses


def evaluate(model, x_test, y_test):
	xt, xf = x_test
	yt, yf = y_test
	
	model.eval() # Set the model to evaluation mode
	losses = []
	song_out = []
	for i in range(0, 50, 5):
		input = (torch.cat(xt[i:i+5], dim=0).to(device), torch.cat(xf[i:i+5], dim=0).to(device))
		target = (torch.cat(yt[i+1:i+4], dim=0).to(device), torch.cat(yf[i+1:i+4], dim=0).to(device))
		output = model(input)
		print(output[0].shape, output[1].shape, target[0].shape, target[1].shape)
		out, loss, is_mel = model.choose_spec_wave(output, target)
	
	print(f"Loss is {loss.item()}")
	dl.save_as_wav("12", )
	
def display_loss(losses):
	plt.plot(losses, label='Training Loss')
	plt.xlabel('Epoch')
	plt.ylabel('Loss')
	plt.legend()
	plt.show()

def normalize_input(x):
	max_track_size = 8_192_000 # 1600 * 5120 ou 6400 * 5120
	res = F.pad(x, (0, max_track_size-x.shape[1])) # padding
	res = res.view(1, 5120, res.shape[1]//5120)
	return res
	
def main():
	# load the dataset
	x_train, y_train, x_test, y_test = dl.get_dataset(subset=True)
	#print(x_train[0][1][0].shape, x_train[1][1].shape, y_train[0][1][0].shape, y_train[1][1].shape, \
	#	x_test[0][1][0].shape, x_test[1][1].shape, y_test[0][1][0].shape, y_test[1][1].shape)
	
	# Divise les tenseurs waveform en 512 chunks de 16000
	x_train = ([normalize_input(t) for t in x_train[0]], [t.view(1, 1280, t.shape[2]//10) for t in x_train[1]])
	y_train = ([normalize_input(t) for t in y_train[0]], [t.view(1, 1280, t.shape[2]//10) for t in y_train[1]])
	x_test = ([normalize_input(t) for t in x_test[0]], [t.view(1, 1280, t.shape[2]//10) for t in x_test[1]])
	y_test = ([normalize_input(t) for t in y_test[0]], [t.view(1, 1280, t.shape[2]//10) for t in y_test[1]])
	
	concatenated_y_train = torch.cat([tensor for tensor in y_train[0]], dim=2)
	y_train = (torch.split(concatenated_y_train, 6400, dim=2), y_train[1])
	concatenated_y_test = torch.cat([tensor for tensor in y_test[0]], dim=2)
	y_test = (torch.split(concatenated_y_test, 6400, dim=2), y_test[1])
	
	#print(len(x_train[0]), len(x_train[0][0]), x_train[0][0][0].shape)
	#print(len(x_train[1]), len(x_train[1][0]), x_train[1][0][0].shape)
	#print(len(y_train[0]), len(y_train[0][0]), y_train[0][0][0].shape)
	#print(len(y_train[1]), len(y_train[1][0]), y_train[1][0][0].shape)
	#print(len(x_test[0]), len(x_test[0][0]), x_test[0][0][0].shape)
	#print(len(x_test[1]), len(x_test[1][0]), x_test[1][0][0].shape)
	#print(len(y_test[0]), len(y_test[0][0]), y_test[0][0][0].shape)
	#print(len(y_test[1]), len(y_test[1][0]), y_test[1][0][0].shape)
	#print(len(x_train), x_train[0].size(), y_train[0].size())
	
	# load the model
	model = load().to(device)
	model.train()
	
	optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
	scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9)

	accelerator = accelerate.Accelerator()
	model, optimizer, scheduler = accelerator.prepare(
		model, optimizer, scheduler
	)
	
	#losses = train(model, x_train, y_train, optimizer, scheduler, accelerator)
	#display_loss(losses)
	#print(x_test)
	evaluate(model, x_test, y_test)
	#torch.chunk(orig_tensor, 4, dim=2)

if __name__ == '__main__':
	main()
