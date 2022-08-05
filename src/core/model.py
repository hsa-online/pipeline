"""
The PyTorch NN Model allowing to compute sum of two input numbers.
   Note: of course it's enough to have a single neuron for that, 
         but we need more realistic NN example.
"""

import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(Model, self).__init__()

        self.fc1 = nn.Linear(input_dim, 20)
        self.fc2 = nn.Linear(20, 20)
        self.output_layer = nn.Linear(20, output_dim)

    def forward(self, x):
       x = F.relu(self.fc1(x))
       x = F.relu(self.fc2(x))
       x = self.output_layer(x)

       return x
