# Usar una imagen base de Python
FROM python:3.12.4

# Establecer el directorio de trabajo

WORKDIR /app/UEC-Flask

# Copiar el archivo de requisitos y la aplicación

COPY . . 
COPY /requirements.txt .

# Instalar dependencias

RUN pip install -r requirements.txt \
&& pip install --upgrade evdev

EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
