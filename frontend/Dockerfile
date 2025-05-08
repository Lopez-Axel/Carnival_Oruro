FROM node:20-alpine

WORKDIR /app

# Copia solo package.json y lock primero para cachear dependencias
COPY package*.json ./

RUN npm install

# El código lo montamos con el volumen, no lo copiamos aquí

EXPOSE 4321
CMD ["npm", "run", "dev"]
