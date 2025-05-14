FROM node:20-alpine

WORKDIR /app

# Copia solo package.json y lock primero para cachear dependencias
COPY package*.json ./

RUN npm install

# El código lo montamos con el volumen, no lo copiamos aquí
EXPOSE 3000
CMD ["astro", "dev", "--host", "0.0.0.0", "--port", "3000"]
# Exponemos el puerto 3000 para el frontend
