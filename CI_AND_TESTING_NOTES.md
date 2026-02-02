# CI & Testing Reference
This document was created by AI* only for understanding and reference purposes.

## GitHub Actions CI

**Minimal workflow structure:**
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.9'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: pytest -q
```

**Matrix testing** (multiple Python versions):
```yaml
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11"]
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

**Critical rules:**
- Always use `cache: 'pip'` for speed
- Pin action versions (`@v4`, never `@latest`)
- Order: fast checks first (lint → test → build)
- Use `pytest -q` for clean CI output

---

## Flask + Pytest Pattern

**Setup (mandatory for non-packaged projects):**
```python
from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import src.app as app_module  # Import MODULE (not just app) for monkeypatching

@pytest.fixture
def client():
    app = app_module.app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
```

**Why import the module?**
```python
# Can't monkeypatch globals
from src.app import app

# Allows monkeypatch.setattr(app_module, 'model', None)
import src.app as app_module
```

---

## Test Coverage Matrix

| Type | Check | Status Code |
|------|-------|-------------|
| Happy path | Valid input → expected output | 200 |
| Bad input | Missing/invalid fields | 400 |
| Method validation | Wrong HTTP method | 405 |
| Server error | Resource unavailable (model not loaded) | 500 |
| Edge cases | Nulls, boundaries, empty strings | varies |

---

## Essential Patterns

### 1. Monkeypatch for Isolation
```python
def test_with_fake_model(client, monkeypatch):
    class FakeModel:
        def predict(self, X):
            return [42.0]
    
    monkeypatch.setattr(app_module, 'model', FakeModel())
    response = client.post('/predict', json={'experience': 5})
    assert response.json['predicted_salary'] == 42.0
```

### 2. Parametrized Tests
```python
@pytest.mark.parametrize('payload', [
    None,                          # No JSON
    {},                            # Empty
    {'experience': None},          # Null value
    {'experience': 'text'},        # Wrong type
])
def test_bad_input(client, monkeypatch, payload):
    monkeypatch.setattr(app_module, 'model', FakeModel())
    response = client.post('/predict', json=payload) if payload else client.post('/predict')
    assert response.status_code == 400
    assert 'error' in response.json
```

### 3. JSON API Testing
```python
response = client.post('/endpoint', json={'key': 'val'})
data = response.get_json()
assert response.status_code == 200
assert data['field'] == expected_value
```

### 4. HTML Route Testing
```python
response = client.get('/')
assert response.status_code == 200
assert 'text/html' in response.content_type
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: src` | Add `sys.path.insert(0, str(PROJECT_ROOT))` |
| Local pass, CI fail | Check Python version, deps, absolute vs relative paths |
| CI timeout on install | Add `cache: 'pip'` to setup-python |
| Slow tests | Monkeypatch instead of real I/O |

**Pytest commands:**
```bash
pytest -q              # Quiet mode
pytest -s              # Show prints
pytest -x              # Stop on first fail
pytest path/file.py::test_name  # Run specific test
```

---

## Testing Checklist

**Flask API:**
- Status codes (200, 400, 405, 500)
- JSON structure matches schema
- Error messages in 400/500 responses
- HTTP method restrictions

**ML Model:**
- Training succeeds + saves file
- Loading works + makes predictions
- Output shape/type correct
- Edge cases (empty, extreme values)

---

## Core Principles

1. **AAA pattern**: Arrange → Act → Assert
2. **Test behavior, not implementation**: Don't test internal private methods
3. **Fast tests**: Mock/fake external dependencies (files, DBs, APIs)
4. **Descriptive names**: `test_predict_returns_400_when_experience_missing`
5. **One focus per test**: Makes failures instantly clear

---

**Updated:** Feb 2026
