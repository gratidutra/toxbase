from flask import Flask, render_template, request, flash
from extractors.extractor import extract_data

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Para mensagens flash no Flask


@app.route("/", methods=["GET", "POST"])
def index():
    results = None

    if request.method == "POST":
        cas_numbers = request.form.get("cas_numbers")
        databases = request.form.getlist("databases")

        if not cas_numbers:
            flash("Por favor, insira um número CAS.", "danger")
        else:
            df_results = extract_data(cas_numbers, databases)

            # Apenas exibe os resultados sem armazenar no banco de dados
            results = {
                cas: {
                    db_name: data.to_html(classes="table table-striped")
                    for db_name, data in dbs.items()
                }
                for cas, dbs in df_results.items()
            }

    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
