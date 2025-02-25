import sys
import os

# Adiciona a pasta src ao caminho do Python para que os módulos possam ser encontrados
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
