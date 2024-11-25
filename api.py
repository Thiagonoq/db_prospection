import json
import os
import base64
import uuid
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Olá, Mundo!"}

@app.post("/response")
async def handle_response(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    with open("response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # Verifica se o campo 'file' existe
    image_base64 = data.get("file")
    if not image_base64:
        raise HTTPException(status_code=400, detail="Campo 'file' ausente no JSON")

    try:
        # Decodifica a string Base64
        image_data = base64.b64decode(image_base64)
    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail="String Base64 inválida")

    # Gera um nome de arquivo único
    filename = f"image_{uuid.uuid4()}.jpg"  # Altere a extensão conforme necessário

    try:
        # Salva a imagem no diretório especificado
        with open(filename, "wb") as image_file:
            image_file.write(image_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao salvar a imagem")

    return {"status": "sucesso", "filename": filename}
