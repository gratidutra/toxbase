# Usa a imagem oficial do Python como base
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos necessários para o container
COPY . /app

# Instala as dependências do sistema operacional
RUN apt-get update && apt-get install -y \
    chromium \
    && apt-get clean

# Atualiza o pip e instala as dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expõe a porta 5000 (a porta padrão do Flask)
EXPOSE 5000

# Define a variável de ambiente para o caminho do Chrome
ENV CHROME_BIN=/usr/bin/chromium


# Dá permissão de execução ao script setup.sh
RUN chmod +x setup.sh

# Executa o setup.sh e depois o Flask
CMD ["bash", "-c", "./setup.sh && python app.py"]