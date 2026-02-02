from pathlib import Path    # For getting the project root
import sys                  # For modifying the system path

import pytest               # For testing framework

# Computes the project root directory by going up 1 folder
PROJECT_ROOT = Path(__file__).resolve().parents[1] 
# Adds the project root to the system path for module imports
sys.path.insert(0, str(PROJECT_ROOT))

import src.app as app_module  # Import the module so we can monkeypatch globals (e.g., model)

app = app_module.app  # Flask application instance

@pytest.fixture
def client():
    app.config['TESTING'] = True  # Enable testing mode for the Flask app
    with app.test_client() as client: # Create a test client fake server
        yield client        # Provide the test client to the test functions

def test_health_check(client):   # Test the health check endpoint
    """Test if the API is up"""  
    response = client.get('/health') # Send a GET request to the /health endpoint
    assert response.status_code == 200 # Check if the response status code is 200 (OK)
    assert response.json['status'] == 'healthy' # Check if the response JSON indicates healthy status
    assert 'model_loaded' in response.json
    assert isinstance(response.json['model_loaded'], bool)


def test_home_page_returns_html(client):    # Test the home page endpoint
    """Test if the home page returns HTML content"""
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.content_type


def test_predict_requires_post(client):
    response = client.get('/predict')
    assert response.status_code == 405


def test_predict_returns_500_when_model_not_loaded(client, monkeypatch):
    monkeypatch.setattr(app_module, 'model', None)
    response = client.post('/predict', json={'experience': 3})
    assert response.status_code == 500
    assert 'error' in response.json


def test_predict_happy_path_with_dummy_model(client, monkeypatch):
    class DummyModel:
        def predict(self, X):
            assert list(X.columns) == ['experience']
            return [12345.6789]

    monkeypatch.setattr(app_module, 'model', DummyModel())
    response = client.post('/predict', json={'experience': 3.5})
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'success'
    assert data['experience_years'] == 3.5
    assert data['predicted_salary'] == 12345.68


@pytest.mark.parametrize(
    'payload',
    [
        None,
        {},
        {'experience': None},
        {'experience': 'not-a-number'},
    ],
)
def test_predict_bad_payload_returns_400(client, monkeypatch, payload):
    class DummyModel:
        def predict(self, X):
            return [1]

    monkeypatch.setattr(app_module, 'model', DummyModel())

    if payload is None:
        response = client.post('/predict')
    else:
        response = client.post('/predict', json=payload)

    assert response.status_code == 400
    assert 'error' in response.json