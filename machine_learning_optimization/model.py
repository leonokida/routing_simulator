import warnings
warnings.filterwarnings("ignore")

import torch
import torch.nn as nn
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GCNConv, global_mean_pool

class LambdaPredictorGNN(torch.nn.Module):
    """
    Architecture of the GNN that predicts the optimal lambda value for MaxFlowRouting given a topology.
    """
    def __init__(self, in_channels: int, hidden_channels: int = 64):
        super().__init__()
        # GNNConv layers
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        
        # Regression layer
        self.lin = nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, batch):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index).relu()
        x = self.conv3(x, edge_index).relu()
        
        # Global mean pooling
        x = global_mean_pool(x, batch)
        
        # Regression
        x = self.lin(x)
        
        # Sigmoid so output is a value between 0 and 1
        return torch.sigmoid(x).squeeze(-1)