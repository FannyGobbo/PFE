import torch
import torch.nn as nn
import torch.nn.functional as F

class ScaleLayer(nn.Module):

   def __init__(self, init_value=1e-3):
	   super().__init__()
	   self.scale = nn.Parameter(torch.FloatTensor([init_value]))

   def forward(self, input):
	   return input * self.scale

class SimpleModel(nn.Module):
	def __init__(self, d_model):
		super(SimpleModel, self).__init__()
		
		f_size = 1600
		t_size = 1600
		print(f_size, f_size, d_model)
		assert d_model <= f_size//20
		assert d_model <= t_size//20

		self.kernel_size = 3
		self.padding = 1
		self.output_tracks = 4
		
		self.fencoder = nn.Sequential(
				nn.Linear(f_size, f_size//2), nn.GELU(),
				#ScaleLayer()
			)
		#self.latent_layer = nn.LSTM(f_size//2, d_model, batch_first=True)
		self.flatent = nn.Sequential(
				nn.Linear(f_size//2, d_model), nn.GELU(),
				nn.Linear(d_model, f_size//20), nn.GELU()
				#nn.LayerNorm(d_model)
			)
		self.fdecoder = nn.Sequential(
				nn.Linear(f_size//20, f_size), nn.GELU(),
				nn.Linear(f_size, f_size*self.output_tracks),
				#ScaleLayer()
			)
		
		self.tencoder = nn.Sequential(
				nn.Linear(t_size, t_size//5), nn.GELU(),
				nn.Linear(t_size//5, t_size//20), nn.GELU(),
				#ScaleLayer()
			)
		#self.latent_layer = nn.LSTM(t_size//2, d_model, batch_first=True)
		self.tlatent = nn.Sequential(
				nn.Linear(t_size//20, d_model),  nn.GELU(),
				nn.Linear(d_model, t_size//20), nn.GELU()
				#nn.LayerNorm(d_model)
			)
		self.tdecoder = nn.Sequential(
				nn.Linear(t_size//20, t_size), nn.GELU(),
				nn.Linear(t_size, t_size*self.output_tracks),
				#ScaleLayer()
			)
	
	def choose_spec_wave(self, output, target):
		#print(output, target, yop)
		l1 = F.mse_loss(output[0], target[0]) * 1_000_000
		l2 = F.mse_loss(output[1], target[1])
		#print(l1, l2)
		
		if min(l1.item(), l2.item()) == l1.item():
			loss = l1
			best = output[0]
			is_mel = False
		else:
			loss = l2 
			best = output[1]
			is_mel = True
		
		return best, loss, is_mel

	def forward(self, x):
		xt, xf = x
		#yt, yf = y
		
		xt = self.tencoder(xt)
		xf = self.fencoder(xf)
		
		#print("1", xt.shape, xf.shape)
		
		xt = self.tlatent(xt) # Returns a tuple (hidden states, mems)
		xf = self.flatent(xf) # Returns a tuple (hidden states, mems)
		
		#print("2", xt.shape, xf.shape)
		
		xf = xf[self.padding : self.padding + self.kernel_size]  # Remove padding
		xt = xt[self.padding : self.padding + self.kernel_size]  # Remove padding
		
		#print("3", xt.shape, xf.shape)
		
		xt = self.tdecoder(xt)
		xf = self.fdecoder(xf)
		
		#xf = torch.cat([xf, xf, xf, xf], dim=2)
		#xt = torch.cat([xt, xt, xt, xt], dim=2)
		
		#print("4", xt.shape, xf.shape)
		return xt, xf

def save (m: nn.Module, name="simple_model"):
	torch.save(m.state_dict(), name+'.pt')

def load (name="simple_model"):
	d_model = 80
	
	m = SimpleModel(d_model)
	#m.load_state_dict(torch.load(name+'.pt'))
	return m

#model = SimpleModel(13000)
#save(model)
