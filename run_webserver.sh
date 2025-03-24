#!/bin/bash

# Carrega as variáveis de ambiente do arquivo .env
source /home/toxbase/.env

# Define a variável de ambiente para o Flask (para garantir que ele use o app correto)
export FLASK_APP=__init__

# Inicia o servidor Flask
flask run --host=0.0.0.0 --port=5000