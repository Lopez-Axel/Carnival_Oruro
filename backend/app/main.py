from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configura CORS para permitir conexiones desde Astro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplaza "*" con tu URL de Astro
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "¡Hola desde FastAPI!", "status": 200}

@app.get("/test")
async def test_endpoint():
    return {"message": "¡Conexión exitosa desde FastAPI!", "status": 200}

@app.get("/data")
async def get_data():
    return {"message": "Aquí tienes algunos datos de ejemplo", "data": [1, 2, 3, 4, 5], "status": 200}