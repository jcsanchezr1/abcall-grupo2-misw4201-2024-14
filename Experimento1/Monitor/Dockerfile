FROM python:3.10.12-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r flaskr/requirements.txt

EXPOSE 5002

# Establece la variable de entorno FLASK_APP a la ubicación correcta del archivo app.py
ENV FLASK_APP=flaskr/app.py

# Comando para iniciar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]
