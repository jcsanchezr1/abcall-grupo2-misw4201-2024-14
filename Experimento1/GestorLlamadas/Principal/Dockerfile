FROM python:3.10.12-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5003

# Establece la variable de entorno FLASK_APP a la ubicación correcta del archivo app.py
ENV FLASK_APP=app.py
ENV PUBSUB_EMULATOR_HOST="pubsub:8120"
ENV PUBSUB_PROJECT_ID="abcall"

# Comando para iniciar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5003"]
