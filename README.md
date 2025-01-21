# ETLXML

## Descripción del Proyecto

ETLXML es un proyecto diseñado para extraer, transformar y cargar datos desde archivos XML. Este proyecto está configurado para funcionar con Docker y Kubernetes, lo que facilita su despliegue en cualquier máquina.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes componentes:

- Docker
- Kubernetes
- Git

## Configuración del Entorno

### Clonar el Repositorio

Primero, clona el repositorio del proyecto:

```bash
git clone https://github.com/david842009/etlxml.git
cd ETLXML
```

### Construir la Imagen de Docker

Construye la imagen de Docker utilizando el archivo `Dockerfile` incluido en el repositorio:

```bash
docker build -t etlxml:latest .
```

### Ejecutar el Contenedor de Docker

Para ejecutar el contenedor de Docker, utiliza el siguiente comando:

```bash
docker run -d --name etlxml-container etlxml:latest
```

## Despliegue en Kubernetes

### Crear un Namespace

Primero, crea un namespace para el proyecto:

```bash
kubectl create namespace etlxml
```

### Aplicar Archivos de Configuración

Aplica los archivos de configuración de Kubernetes que se encuentran en el directorio `k8s`:

```bash
kubectl apply -f k8s/ -n etlxml
```

### Verificar el Despliegue

Verifica que los pods estén corriendo correctamente:

```bash
kubectl get pods -n etlxml
```

## Configuración Adicional

### Variables de Entorno

Asegúrate de configurar las variables de entorno necesarias en los archivos de configuración de Docker y Kubernetes. Estas variables incluyen:

- `DB_HOST`: Dirección del host de la base de datos
- `DB_USER`: Usuario de la base de datos
- `DB_PASS`: Contraseña de la base de datos

Estas variables se encuentran dentro del manifiesto deployment.yaml y deberan ser iguales a las del despliegue de la imagen del contenedor de base de datos