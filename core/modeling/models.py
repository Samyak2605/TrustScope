import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import numpy as np
import joblib
import os

class SimpleNN(nn.Module):
    """
    A simple MLP with Dropout for Monte Carlo Dropout uncertainty estimation.
    """
    def __init__(self, input_dim):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.dropout1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, 32)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout1(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.sigmoid(self.fc3(x))
        return x

class TrustModelManager:
    """
    Manages an ensemble of models for prediction and subsequent trust analysis.
    """
    def __init__(self, input_dim, model_dir="data/models"):
        self.input_dim = input_dim
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.lr_model = LogisticRegression(max_iter=1000)
        self.nn_model = SimpleNN(input_dim)
        
        self.is_trained = False

    def train(self, X_train, y_train):
        print("[TrustModelManager] Training ensemble models...")
        
        # Train Random Forest
        self.rf_model.fit(X_train, y_train)
        
        # Train Logistic Regression
        self.lr_model.fit(X_train, y_train)
        
        # Train Neural Network
        X_tensor = torch.FloatTensor(X_train)
        y_tensor = torch.FloatTensor(y_train).view(-1, 1)
        
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.nn_model.parameters(), lr=0.001)
        
        self.nn_model.train()
        for epoch in range(100):
            optimizer.zero_grad()
            outputs = self.nn_model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
        
        self.is_trained = True
        self.save_models()
        print("[TrustModelManager] Ensemble training complete.")

    def save_models(self):
        joblib.dump(self.rf_model, os.path.join(self.model_dir, "rf_model.joblib"))
        joblib.dump(self.lr_model, os.path.join(self.model_dir, "lr_model.joblib"))
        torch.save(self.nn_model.state_dict(), os.path.join(self.model_dir, "nn_model.pth"))

    def load_models(self):
        self.rf_model = joblib.load(os.path.join(self.model_dir, "rf_model.joblib"))
        self.lr_model = joblib.load(os.path.join(self.model_dir, "lr_model.joblib"))
        self.nn_model.load_state_dict(torch.load(os.path.join(self.model_dir, "nn_model.pth")))
        self.is_trained = True

    def predict_all(self, X_input):
        """
        Returns predictions and probabilities from all models in the ensemble.
        """
        if not self.is_trained:
            self.load_models()

        X_tensor = torch.FloatTensor(X_input)
        
        # RF Predictions
        rf_prob = self.rf_model.predict_proba(X_input)[:, 1]
        
        # LR Predictions
        lr_prob = self.lr_model.predict_proba(X_input)[:, 1]
        
        # NN Predictions (Evaluation mode)
        self.nn_model.eval()
        with torch.no_grad():
            nn_prob = self.nn_model(X_tensor).numpy().flatten()
            
        return {
            'rf': rf_prob,
            'lr': lr_prob,
            'nn': nn_prob
        }
