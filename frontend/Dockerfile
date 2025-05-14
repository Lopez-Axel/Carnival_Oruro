FROM node:20-alpine

WORKDIR /app

# Copiar las dependencias
COPY package*.json ./
RUN npm install

# Copiar el resto del proyecto
COPY . .

# Render espera que la app escuche en PORT (puerto 3000 por defecto)
ENV PORT=3000
EXPOSE 3000

# Usamos Astro desde npx y le especificamos el puerto y host
CMD ["npx", "astro", "dev", "--host", "0.0.0.0", "--port", "3000"]
