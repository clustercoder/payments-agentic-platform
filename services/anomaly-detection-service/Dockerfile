# ---- Base image ----
FROM python:3.11-slim

# ---- System-level optimizations ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Set working directory ----
WORKDIR /app

# ---- Install OS dependencies (minimal) ----
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---- Install Python dependencies first (cache-friendly) ----
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Copy application code ----
COPY app ./app

# ---- Expose port (FastAPI health / metrics later) ----
EXPOSE 8002

# ---- Run the service ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
