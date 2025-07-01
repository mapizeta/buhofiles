# Buhofiles
flask run --host=0.0.0.0 --port=5000 --debug

# Construir la imagen
docker build -t buhofiles .

# Ejecutar con Docker
docker run -p 5000:5000 buhofiles

# O usar Docker Compose (recomendado)
docker-compose up --build
