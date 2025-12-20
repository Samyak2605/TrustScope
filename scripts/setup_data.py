import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from core.data_science.profiler import DataProfiler
from core.modeling.models import TrustModelManager
import joblib
import os

def setup():
    print("[Setup] Loading TRUSTSCOPE Pilot Dataset (Breast Cancer)...")
    data = load_breast_cancer()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)

    # 1. Fit Data Profiler
    profiler = DataProfiler()
    profiler.fit_distribution(X_train)
    joblib.dump(profiler, "data/profiler.joblib")

    # 2. Train Models
    manager = TrustModelManager(input_dim=X_train.shape[1])
    manager.train(X_train.values, y_train)

    # 3. Save test data for later verification
    X_test.to_csv("data/test_features.csv", index=False)
    pd.Series(y_test, name="target").to_csv("data/test_labels.csv", index=False)

    print("[Setup] Data environment ready.")

if __name__ == "__main__":
    setup()
