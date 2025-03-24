# Usa a imagem oficial do Python como base
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /home/toxbase

# Copia o arquivo .env para o container
COPY .env /home/toxbase/.env

# Copia apenas o arquivo requirements.txt primeiro para otimizar cache
COPY requirements.txt /home/toxbase/requirements.txt

# Instala dependências do sistema operacional
RUN apt-get update && apt-get install -y \
    chromium \
    && apt-get clean

# Instala as dependências do Python
RUN pip install --upgrade pip && \
    pip install -r /home/toxbase/requirements.txt

# Agora copia o restante dos arquivos do projeto
COPY . /home/toxbase

# Dá permissão de execução para o script run.sh
RUN chmod +x /home/toxbase/run_webserver.sh

# Define o diretório onde está o código-fonte
WORKDIR /home/toxbase/src

# Expõe a porta 5000 (padrão do Flask)
EXPOSE 5000

# Define a variável de ambiente para o caminho do Chrome
ENV CHROME_BIN=/usr/bin/chromium

# Define o comando final para rodar a aplicação
CMD ["/bin/bash", "/home/toxbase/run_webserver.sh"]
