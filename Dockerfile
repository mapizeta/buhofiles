FROM python:3.9-slim

WORKDIR /app

# Instalar ffmpeg y otras dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear la carpeta de descargas si no existe
RUN mkdir -p /app/app/static/downloads

EXPOSE 5000

CMD ["python", "run.py"] 