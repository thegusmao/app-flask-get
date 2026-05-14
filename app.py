import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Lê a URL da variável de ambiente ao iniciar
TARGET_URL = os.environ.get('TARGET_URL')
TIMEOUT = os.environ.get('TIMEOUT')

@app.route('/fetch', methods=['GET'])
def fetch_from_env():
    if not TARGET_URL:
        return jsonify({"error": "A variável de ambiente 'TARGET_URL' não foi definida."}), 500

    try:
        # Suporta tanto http quanto https automaticamente
        response = requests.get(TARGET_URL, verify=False, timeout=TIMEOUT)
        return (response.content, response.status_code, response.headers.items())
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Falha ao conectar em {TARGET_URL}: {str(e)}"}), 500

if __name__ == '__main__':
    # O OpenShift geralmente usa a porta 8080 por padrão para usuários não-root
    app.run(host='0.0.0.0', port=8080)
