# Imagen base
FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar las dependencias
COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código del pipeline
COPY src /app/src

# Comando predeterminado para ejecutar el pipeline
ENTRYPOINT ["python", "/app/src/etl_pipeline.py"]
