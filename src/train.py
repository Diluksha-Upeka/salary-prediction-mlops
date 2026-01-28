import pandas as pd
import joblib   # For saving the model
from sklearn.linear_model import LinearRegression
import os

# Define paths
DATA_PATH = "data/salaries.csv"     # Path to your training data
MODEL_DIR = "model"                 # Directory to save the model
MODEL_PATH = os.path.join(MODEL_DIR, "salary_model.pkl") # Model file path

def train():
    print("Starting training pipeline...")
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data not found at {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)  # Load your training data
    
    # 2. Preprocessing
    # Rename columns for consistency
    if 'YearsExperience' in df.columns:
        df = df.rename(columns={"YearsExperience": "experience", "Salary": "salary"})
    
    X = df[['experience']]  # Features
    y = df['salary']        # Target variable
    
    # 3. Train Model
    model = LinearRegression()      # Initialize the model
    model.fit(X, y)                 # Train the model
    print(f"Model trained. Coefficients: {model.coef_}")  # Print model coefficients

    # 4. Save Model
    os.makedirs(MODEL_DIR, exist_ok=True)  # Create model directory if it doesn't exist
    joblib.dump(model, MODEL_PATH)         # Save the trained model
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":          # Ensure this script is executed directly
    train()