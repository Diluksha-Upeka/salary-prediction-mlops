# salary-prediction-mlops

Minimal salary prediction project scaffold.

## Project layout
- `data/salaries.csv` — training data
- `src/train.py` — trains a simple model and saves it to `model/model.joblib`
- `src/app.py` — FastAPI service that loads the model and serves predictions
- `tests/test_api.py` — basic API tests

## Quickstart (local)
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Train (optional)
python src/train.py

# Run API
python -m uvicorn src.app:app --reload
```

## Quickstart (Docker)
```bash
docker build -t salary-prediction .
docker run -p 8000:8000 salary-prediction
```

## API
- `GET /health`
- `POST /predict` with JSON: `{ "years_experience": 5 }`
