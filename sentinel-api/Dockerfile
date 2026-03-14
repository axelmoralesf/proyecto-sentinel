# 1. Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Crear una carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar la lista de dependencias
COPY requirements.txt .

# 4. Instalar las dependencias exactas que acabas de congelar
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código de la API al contenedor
COPY . .

# 6. Abrir el puerto 8000 para que la API pueda comunicarse
EXPOSE 8000

# 7. El comando de arranque cuando se encienda el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]