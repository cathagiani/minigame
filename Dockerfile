# Usar una imagen de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que Flask va a correr
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "app.py"]
