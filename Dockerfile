# Dockerfile pour le service FastAPI et Streamlit

FROM python:3.10-slim

WORKDIR /app

# Préférer pip en sidestepping cache
RUN python -m pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "src.energystock_ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
