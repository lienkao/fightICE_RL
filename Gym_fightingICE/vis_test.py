import torch
from torch import nn

from torchviz import make_dot, make_dot_from_trace
model = nn.Sequential()

model.add_module('W0', nn.Linear(8, 16))
model.add_module('tanh', nn.Tanh())
model.add_module('W1', nn.Linear(16, 1))

x = torch.randn(1,8)

make_dot(model(x), params=dict(model.named_parameters()))
v=make_dot(model(x), params=dict(model.named_parameters()), show_attrs=True, show_saved=False)
v.view()