# Training of ML model to predict optimal lambda for MaxFlowRouting given a topology
# Author: Leon Okida
# Last modification: 10/25/2026

# Ignore PyTorch warning
import warnings
warnings.filterwarnings("ignore")

from machine_learning_optimization.model import LambdaPredictorGNN

import torch
import torch.nn as nn
from torch_geometric.loader import DataLoader

# --- 1. Dataset and DataLoaders ---
# Loads dataset
dataset = torch.load("machine_learning_optimization/dataset/routing_optimization_dataset.pt", weights_only=False)

print(f"Graphs in the dataset: {len(dataset)}")
for i, data in enumerate(dataset[:5]):
    print(f"Graph {i+1} -> Size: {data.num_nodes}, Edges: {data.num_edges // 2}, Optimal Lambda found: {data.y.item():.2f}")
print("...")

# Shuffle and split into training (80%) and test (20%) sets
torch.manual_seed(0)
dataset = list(dataset)
import random
random.shuffle(dataset)

train_size = int(0.8 * len(dataset))
train_dataset = dataset[:train_size]
test_dataset = dataset[train_size:]

# PyG DataLoader
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# --- 2. Training settings ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = LambdaPredictorGNN(in_channels=dataset[0].num_node_features, hidden_channels=64).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

# --- 3. Training with Early Stopping & Best Model Checkpointing ---
epochs = 1000
patience = 100
best_val_loss = float('inf')
patience_counter = 0

for epoch in range(1, epochs + 1):
    model.train()
    total_train_loss = 0
    
    for batch in train_loader:
        batch = batch.to(device)
        optimizer.zero_grad()
        
        # Forward pass
        out = model(batch.x, batch.edge_index, batch.batch)
        loss = criterion(out, batch.y.view(-1))

        # Backpropagation
        loss.backward()
        optimizer.step()
        
        total_train_loss += loss.item() * batch.num_graphs
        
    train_loss = total_train_loss / len(train_dataset)
    
    # --- Validation ---
    model.eval()
    total_val_loss = 0
    with torch.no_grad():
        for batch in test_loader:
            batch = batch.to(device)
            out = model(batch.x, batch.edge_index, batch.batch)
            val_loss = criterion(out, batch.y.view(-1))
            total_val_loss += val_loss.item() * batch.num_graphs
            
    val_loss = total_val_loss / len(test_dataset)
    
    # --- Logs ---
    if epoch % 10 == 0 or epoch == 1:
        print(f"Epoch {epoch:03d}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        
    # --- Early Stopping and Checkpoint ---
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0  # Resets the counter if there's an improvement
        # Saves the best model so far
        torch.save(model.state_dict(), "machine_learning_optimization/model/best_lambda_predictor_gnn.pth")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"\nEarly stopping on epoch {epoch}!")
            print(f"Best Val Loss achieved: {best_val_loss:.4f}")
            break

print("Training finished. The best model was saved as 'machine_learning_optimization/model/best_lambda_predictor_gnn.pth'.")