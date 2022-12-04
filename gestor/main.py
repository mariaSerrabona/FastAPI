from fastapi import FastAPI, Response,HTTPException
from fastapi.responses import JSONResponse
import database as db
import uvicorn
import helpers
import  pydantic
from helpers import dni_valido

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/html/")
def html():
    content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>¡Hola mundo!</title>
    </head>
    <body>
        <h1>¡Hola mundo!</h1>
    </body>
    </html>
    """
    return Response(content=content, media_type="text/html")



@app.get("/clientes/")
async def clientes():
    content = [
    {'dni': cliente.dni, 'nombre': cliente.nombre, 'apellido': cliente.apellido}
        for cliente in db.Clientes.lista]
    headers = {"content-type": "charset=utf-8"}
    return JSONResponse(content=content, headers=headers)


@app.get("/clientes/buscar/{dni}/")
async def clientes_buscar(dni: str):
    cliente = db.Clientes.buscar(dni=dni)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    #headers = {"content-type": "charset=utf-8"}
    return cliente


class ModeloCliente(pydantic.BaseModel):
    dni: str=pydantic.Field(min_length=3, max_length=3)
    nombre: str=pydantic.Field(min_length=2, max_length=30)
    apellido: str=pydantic.Field(min_length=2, max_length=30)

class ModeloCrearCliente(ModeloCliente):
    #@dni_valido("dni", db.Clientes.lista)
    def validar_dni(self, dni):
        if not helpers.dni_valido(dni, db.Clientes.lista):
            raise ValueError("Cliente ya existente o DNI incorrecto")
        return dni



@app.post("/clientes/crear/")
async def clientes_crear(datos: ModeloCrearCliente):
    cliente = db.Clientes.crear(datos.dni, datos.nombre, datos.apellido)
    if cliente:
        #headers = {"content-type": "charset=utf-8"}
        #JSONResponse(content=content.to_dict(), headers=headers)
        return cliente
    raise HTTPException(status_code=404)


@app.delete("/clientes/borrar/{dni}/")
async def clientes_borrar(dni: str):
    if db.Clientes.buscar(dni=dni):
        cliente = db.Clientes.borrar(dni=dni)
        headers = {"content-type": "charset=utf-8"}
        #JSONResponse(content=cliente.to_dict(), headers=headers)
        content=[{'dni': cliente.dni, 'nombre': cliente.nombre, 'apellido': cliente.apellido}
        for cliente in db.Clientes.lista]
        return content
    raise HTTPException(status_code=404)

print("Servidor de la API...")

if __name__ == "__main__":
    uvicorn.run(app,host= '0.0.0.0', port=8000)