# salary-prediction-mlops

This project demonstrates a complete Machine Learning Lifecycle from training a Linear Regression model to deploying a containerized API in the cloud. It features a CI/CD pipeline with GitHub Actions for automated testing and uses Docker to ensure production consistency.

## Folder structure (what’s where)
- `data/salaries.csv` — the dataset
- `src/train.py` — trains the model and saves it into the `model/` folder
- `src/app.py` — Flask app (serves the UI + API)
- `src/templates/index.html` — the frontend page (Tailwind CSS)
- `model/` — trained model file gets saved here (generated)
- `tests/test_api.py` — quick pytest checks

## Run it locally
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# 1) Train the model
python src/train.py

# 2) Start the web app
python src/app.py
```

Open your browser:
- UI: `http://127.0.0.1:5000/`
- Health check: `http://127.0.0.1:5000/health`

## API endpoints
- `GET /health`
	- Returns something like: `{ "status": "healthy", "model_loaded": true }`

- `POST /predict`
	- JSON body example: `{ "experience": 3.5 }`
	- Returns something like:
		- `{ "status": "success", "experience_years": 3.5, "predicted_salary": 12345.67 }`

## Run with Docker
```bash
docker build -t salary-prediction .
docker run -p 5000:5000 salary-prediction
```

Then open: `http://127.0.0.1:5000/`

## Run tests
```bash
pytest -q
```
