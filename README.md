# abcall-grupo2-misw4201-2024-14
## Repositorio utilizado para gestión de los experimentos de la materia Arquitecturas agiles de software

Integrantes:
| Nombre          | Correo |
| --------------- |-------------|
| Ian Beltran     | ip.beltran@uniandes.edu.co |
| Sergio Celis    | s.celise@uniandes.edu.co |
| Diego Jaramillo | df.jaramilloa1@uniandes.edu.co |
| Julio Sanchez   | jc.sanchezr1@uniandes.edu.co |

## Prerrequisitos Generales
Tener instalado previamente las siguientes herramientas/software:

- Docker
- Git
- Python
- Apache-jmeter-5.6.3

## Experimento 1

### Microservicio GestorLlamadas

Para desplegar el contenedor de GestorLlamadas pricipal y redundante, siga estos pasos:

1. Ubicarse en la raíz de la carpeta Experimento1: (`cd Experimento1/`)
2. Ejecutar el comando para levantar el contenedor de Principal: `docker compose up -d principal`
3. Ejecutar el comando para levantar el contenedor de Redundante: `docker compose up -d redundante`

### Microservicio Monitor

Este componente estará encargado de consumir los healthchecks para validar el estado de salud de los componentes GestorLlamadas Principal y Redundante. Esta información la almecanará en una base de datos para entregársela al componente Receptor cuando la solicite.

Para desplegar el contenedor de Monitor, siga estos pasos:

1. Ubicarse en la raíz de la carpeta Experimento1: (`cd Experimento1/`)
2. Ejecutar el comando para levantar el contenedor de Monitor: `docker compose up -d monitor`

Si queremos conectarnos a la base de datos del contenedor Monitor ejecutar los siguientes comandos:
1. `docker exec -it experimento1-monitor-1 /bin/bash`
2. `sqlite3 /app/instance/healtchecks.db`


### Microservicio Receptor

Para desplegar el contenedor de Receptor, siga estos pasos:

1. Ubicarse en la raíz de la carpeta Experimento1: (`cd Experimento1/`)
2. Ejecutar el comando para levantar el contenedor de Receptor: `docker compose up -d receptor`

Si queremos conectarnos a la base de datos del contenedor Receptor ejecutar los siguientes comandos:
1. `docker exec -it experimento1-receptor-1 /bin/bash`
2. `sqlite3 /app/instance/experimento_abcall.db`

### Mockserver
Este componente simulará las llamadas de healthcheck de los componentes GestorLlamadas Principal y Redundante, y también incluye un mock del servicio de gestión de llamadas (/call).
Para levantarlo de manera local, seguir los siguientes pasos:

1. Ubicarse en la raíz de la carpeta Experimento1: (`cd Experimento1/`)
2. Ejecutar el comando para levantar el contenedor de Mockserver: `docker compose up -d mockserver`

### PubSub
Estamos usando el emulador de Pub/Sub que es un servicio de GCP de mensajería escalable y asíncrono que separa los servicios que producen mensajes de los que los procesan.
Para levantarlo de manera local, estamos utilizando el emulador de PubSub con ayuda de Docker:

Iniciar y ejecutar el emulador de Pub/Sub (ubicarse en el mismo directorio que contiene el archivo docker-compose.yml `cd Experimento1/`)

`docker compose up -d pubsub`

#### Creacion topicos y subscripciones en el emulador de PubSub

En el archivo `gcp-pubsub-request.http` se definen los topicos y subscripciones para la ejecución del experimento, para ello se recomienda ejecutarlo desde un IDE.
Se recomienda usar Intellij el cual soporta la ejecución de archivos `.http`

1. Abrir el archivo `gcp-pubsub-request.http` desde el IDE Intellij
2. Seleccionar el ambiente local. Este fue creado previamente y está especificado en el archivo `http-client.env.json`
3. Hacer click en el boton de **Run All Request in File**, esto ejecutará las peticiones para la creacion de los topicos y subscripciones
4. Un panel se abrirá automáticamente mostrando la respuesta HTTP para cada solicitud, incluyendo el código de estado y el cuerpo de la respuesta
5. Asegurarse de que todas las solicitudes ejecutadas hayan finalizado correctamente y que el código de estado HTTP 200 esté presente en cada una de ellas, lo que confirmará que los tópicos y suscripciones se han creado exitosamente.

### Importar script de ejecución Apache-jmeter

En el archivo `Script Plan Pruebas Experimento 1.jmx` se encuentra el plan de pruebas del experimento.

### Comandos para exportar la data desde el contenedor receptor

1. Conectarse a sqlite desde el contenedor receptor

```
docker exec -it experimento1-receptor-1 /bin/bash
sqlite3 /app/instance/experimento_abcall.db
```

2. Exportar la data a un archivo csv

```
.mode csv
.output /app/instance/salida_final.csv
SELECT au.*, ((julianday(au.fecha_finalizacion) - julianday(au.fecha_registro)) * 86400000) as diferencia FROM auditoria au;
```

3. Enviar el archivo a una ruta específica por fuera del contenedor
```
docker cp experimento1-receptor-1:/app/instance/salida_final.csv /path/salida
```
Nota: `/path/salida` es la ruta donde se quiere exportar el reporte

## Experimento 2

### Microservicio GestorIncidentes

Para desplegar el contenedor de GestorIncidentes, siga estos pasos:

1. Ubicarse en la raíz de la carpeta Experimento2: (`cd Experimento2/`)
2. Ejecutar el comando para levantar el contenedor de GestorIncidentes: `docker compose up -d incidente`

### Microservicio ReceptorVerificador

Para desplegar el contenedor de Receptor, siga estos pasos:

1. Ubicarse en la raíz de la carpeta Experimento2: (`cd Experimento2/`)
2. Ejecutar el comando para levantar el contenedor de Receptor: `docker compose up -d receptor_verificador`

### PubSub
Estamos usando el emulador de Pub/Sub que es un servicio de GCP de mensajería escalable y asíncrono que separa los servicios que producen mensajes de los que los procesan.
Para levantarlo de manera local, estamos utilizando el emulador de PubSub con ayuda de Docker:

Iniciar y ejecutar el emulador de Pub/Sub (ubicarse en el mismo directorio que contiene el archivo docker-compose.yml `cd Experimento2/`)

`docker compose up -d pubsub`

#### Creacion topicos y subscripciones en el emulador de PubSub

En el archivo `gcp-pubsub-request.http` se definen los topicos y subscripciones para la ejecución del experimento, para ello se recomienda ejecutarlo desde un IDE.
Se recomienda usar Intellij el cual soporta la ejecución de archivos `.http`

1. Abrir el archivo `gcp-pubsub-request.http` desde el IDE Intellij
2. Seleccionar el ambiente local. Este fue creado previamente y está especificado en el archivo `http-client.env.json`
3. Hacer click en el boton de **Run All Request in File**, esto ejecutará las peticiones para la creacion de los topicos y subscripciones
4. Un panel se abrirá automáticamente mostrando la respuesta HTTP para cada solicitud, incluyendo el código de estado y el cuerpo de la respuesta
5. Asegurarse de que todas las solicitudes ejecutadas hayan finalizado correctamente y que el código de estado HTTP 200 esté presente en cada una de ellas, lo que confirmará que los tópicos y suscripciones se han creado exitosamente.

### Comandos para exportar la data desde el contenedor receptor_verificador

1. Conectarse a sqlite desde el contenedor receptor_verificador

```
docker exec -it experimento2-receptor_verificador-1 /bin/bash
sqlite3 /app/instance/experimento2_abcall.db
```

2. Exportar la data a un archivo csv

```
.mode csv
.output /app/instance/salida_final.csv
SELECT au.*, ((julianday(au.fecha_finalizacion) - julianday(au.fecha_registro)) * 86400000) as diferencia FROM auditoria au;
```

3. Enviar el archivo a una ruta específica por fuera del contenedor
```
docker cp experimento2-receptor_verificador-1:/app/instance/salida_final.csv /path/salida
```
Nota: `/path/salida` es la ruta donde se quiere exportar el reporte

