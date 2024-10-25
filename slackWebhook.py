import requests as req
import json
import os
from dotenv import load_dotenv

load_dotenv()

def enviar(mensagem):
    # URL da API Slack
    url = os.getenv("URL_SLACK")
    # JSON da Mensagem
    payload = {"text": mensagem}
    # Cabeçalho HTTP
    headers = {"Content-Type":"application/json"}
    # Efetuação da chamada HTTP [POST] para o Slack
    resposta = req.post(url, data=json.dumps(payload),headers=headers)

    if resposta.status_code == 200:
        return "Mensagem enviada com sucesso!"
    else:
        return f"Erro ao enviar mensagem: {resposta.status_code}"