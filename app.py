from flask import Flask, render_template, request, flash, Response
import pandas as pd
from extractors.extractor import extract_data  # Importa as funções de extração

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET", "POST"])
def index():
    results = None  # Para armazenar os DataFrames convertidos

    if request.method == "POST":
        cas_numbers = request.form.get("cas_numbers")
        databases = request.form.getlist("databases")  # Obtém lista de bancos selecionados

        if not cas_numbers:
            flash("Please enter toxin IDs in the text area above.", "danger")
        else:
            # Chama a função de extração, que retorna um dicionário de DataFrames
            df_results = extract_data(cas_numbers, databases)

            # Converte os DataFrames para HTML para exibição na página
            results = {cas: {db: df.to_html(classes='table table-striped') for db, df in dbs.items()} for cas, dbs in df_results.items()}

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
