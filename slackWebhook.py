import requests as req
import json
import os
from dotenv import load_dotenv

load_dotenv()

def enviarMensagem(mensagem):
    url = os.getenv("URL_SLACK")
    payload = {"text": mensagem}
    headers = {"Content-Type":"application/json"}
    resposta = req.post(url, data=json.dumps(payload),headers=headers)

    if resposta.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Erro ao enviar mensagem: {resposta.status_code}")