"""API tests for the Flask app.

These tests use Flask's built-in test client, which lets us call endpoints like
client.get('/health') without running a real server.
"""

from pathlib import Path    # For computing the project root
import sys                  # For adjusting Python's import path during tests

import pytest               # For testing framework

# Compute the repository root directory by going up from tests/ to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Add the project root to sys.path so imports like `import src.app` work even when
# the project isn't installed as a package.
sys.path.insert(0, str(PROJECT_ROOT))

import src.app as app_module

# IMPORTANT:
# We import the *module* (src.app), not just the Flask app object.
# That allows monkeypatching module-level globals like `model` in tests.

app = app_module.app  # Flask application instance

@pytest.fixture
def client():
    """Flask test client fixture.

    - Sets Flask into TESTING mode (better error reporting for tests)
    - Creates a lightweight HTTP client for making requests to the app
    - Yields it to each test that asks for `client`
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """GET /health returns a 200 and a small JSON status payload."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert 'model_loaded' in response.json
    assert isinstance(response.json['model_loaded'], bool)


def test_home_page_returns_html(client):
    """GET / returns HTML (the UI page)."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.content_type


def test_predict_requires_post(client):
    """/predict should reject GET; it only supports POST."""
    response = client.get('/predict')
    assert response.status_code == 405

def test_predict_returns_500_when_model_not_loaded(client, monkeypatch):  
    """If the model isn't loaded, /predict should fail with a server error.

    monkeypatch: pytest helper that temporarily changes attributes during a test.
    Here we set src.app.model = None to simulate "model file missing/not loaded".
    """
    monkeypatch.setattr(app_module, 'model', None)
    response = client.post('/predict', json={'experience': 3})
    assert response.status_code == 500
    assert 'error' in response.json


def test_predict_happy_path_with_dummy_model(client, monkeypatch):
    """Happy path: valid JSON payload returns a successful prediction.

    We use a DummyModel to avoid depending on a real trained model file.
    This keeps tests fast and deterministic.
    """
    class DummyModel:
        def predict(self, X):
            # src/app.py builds a DataFrame with a single feature column: "experience".
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
    """Bad inputs should return a 400 with an error message.

    Parametrized test:
    - pytest runs this same test multiple times with different `payload` values
    - each payload becomes its own test case in the output
    """
    class DummyModel:
        def predict(self, X):
            return [1]

    monkeypatch.setattr(app_module, 'model', DummyModel())

    # If no JSON is sent at all, request.get_json() returns None and the route should
    # fall into the exception handler and return a 400.
    if payload is None:
        response = client.post('/predict')
    else:
        response = client.post('/predict', json=payload)

    assert response.status_code == 400
    assert 'error' in response.json