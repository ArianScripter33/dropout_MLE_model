import pandas as pd
import os
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report

# Simulate running from notebooks directory
os.chdir('/Users/arianstoned/Desktop/dropout_MLE_model/notebooks')

print("Current working directory:", os.getcwd())

try:
    # 1. Load Data
    df = pd.read_parquet('../data/processed/preprocessed_data.parquet')
    print(f"Data loaded successfully. Shape: {df.shape}")
    
    # 2. Prepare Data
    X = df.drop('Target', axis=1)
    y = df['Target'].apply(lambda x: 1 if x == 'Dropout' else 0)
    
    # Fix: Encode categorical variables
    X = pd.get_dummies(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Train Model
    print("Training XGBoost model...")
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    model.fit(X_train, y_train)
    
    # 4. Predict and Report
    y_pred = model.predict(X_test)
    
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=['No Dropout', 'Dropout']))
    
except Exception as e:
    print(f"Error: {e}")
