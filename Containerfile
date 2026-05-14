# Usando a imagem base do UBI9 (Universal Base Image da Red Hat)
FROM registry.access.redhat.com/ubi9/python-312:latest

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY app.py .

# O OpenShift roda containers com usuários aleatórios, 
# por isso expomos a porta 8080 (não-root)
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
