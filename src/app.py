from flask import Flask, request, jsonify, render_template  # Flask framework
import joblib
import pandas as pd
import os

app = Flask(__name__, template_folder='templates')  # Initialize Flask app with templates folder

MODEL_PATH = "model/salary_model.pkl"  # Path to the trained model

# Load model at startup
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None


@app.route('/')  # Define the root route
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model:        # Check if the model is loaded
        return jsonify({"error": "Model not loaded. Train first."}), 500
    
    try:                # Get input data from request
        data = request.get_json()  # Expecting JSON input
        experience = float(data['experience']) # Extract years of experience
        
        # Prediction (use DataFrame to match training feature names)
        X = pd.DataFrame({"experience": [experience]})
        prediction = model.predict(X)[0]
        
        # Response format
        return jsonify({    
            "status": "success",
            "experience_years": experience,
            "predicted_salary": round(prediction, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Health Check Endpoint ensuring the API is running
@app.route('/health', methods=['GET'])  
def health():
    return jsonify({"status": "healthy", "model_loaded": model is not None})

# Run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)