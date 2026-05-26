import os
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Configurações via ENV
TARGET_URL = os.environ.get('TARGET_URL')
TIMEOUT = float(os.environ.get('TIMEOUT', 10))
# Captura o nome do pod atual
POD_NAME = os.environ.get('HOSTNAME', 'pod-desconhecido')

HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length", "content-encoding",
}

@app.route('/fetch', methods=['GET', 'POST'])
def fetch_and_forward():
    if not TARGET_URL:
        return jsonify({"error": "TARGET_URL não definida"}), 500

    # 1. Prepara os Headers
    excluded_headers = ['Host', 'Content-Length']
    forward_headers = {k: v for k, v in request.headers if k not in excluded_headers}
    
    # 2. Lógica de Histórico do Cabeçalho
    # Se o header já existir, movemos o valor para o 'X-Original'
    existing_forward = request.headers.get('X-Forwarded-From-Pod')
    if existing_forward:
        forward_headers['X-Original-Forwarded-From-Pod'] = existing_forward

    # 3. Adiciona o nome do Pod atual no header principal
    forward_headers['X-Forwarded-From-Pod'] = POD_NAME

    # 4. Captura o Body original
    forward_data = request.get_data()

    try:
        # 5. Faz a chamada ao destino
        response = requests.request(
            method=request.method,
            url=TARGET_URL,
            headers=forward_headers,
            data=forward_data,
            verify=False,
            timeout=TIMEOUT
        )
        
        safe_headers = [
            (k, v) for k, v in response.headers.items()
            if k.lower() not in HOP_BY_HOP
        ]
        
        return (response.content, response.status_code, safe_headers)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Falha no encaminhamento", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
