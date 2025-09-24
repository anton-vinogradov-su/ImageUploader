FROM python:3.12-slim as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libjpeg-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

EXPOSE 8000

# For development use: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# .dockerignore recommendations:
# __pycache__
# *.pyc
# *.pyo
# *.pyd
# .Python
# env/
# build/
# develop-eggs/
# dist/
# downloads/
# eggs/
# .eggs/
# lib/
# lib64/
# parts/
# sdist/
# var/
# *.egg-info/
# .installed.cfg
# *.egg
# .venv/
# .env
# .vscode/
# .pytest_cache/