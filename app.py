from flask import Flask, render_template, request, flash
from src.database import connection_db
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

            # Conectar ao banco de dados
            conn, cursor = connection_db()
            if conn is None or cursor is None:
                flash("Erro ao conectar ao banco de dados.", "danger")
                return render_template("index.html", results=None)

            try:
                for cas, dbs in df_results.items():
                    for db_name, data in dbs.items():
                        if db_name == "PubChem":
                            for _, row in data.iterrows():
                                cursor.execute(
                                    """
                                    INSERT INTO pubchem (cas_number, cit, molecular_formula, 
                                                         synonyms, molecular_weight, dates, 
                                                         description, created_date, updated_date)
                                    VALUES (%s, %s, %s, %s, %s, %s,%s, NOW(), NOW())
                                    """,
                                    (row['CAS Number'], row['CID'], row['Fórmula Molecular'], 
                                     row['Sinônimos'], row['Peso Molecular'], row['Datas'], 
                                     row['Descrição'])
                                )

                        elif db_name == "ECHA":
                            for _, row in data.iterrows():
                                cursor.execute(
                                    """
                                    INSERT INTO echa (cas_number, ec, molecular_formula, 
                                                      haz_classification, about_1, 
                                                      about_2, consumer_user, created_date, updated_date)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                                    """,
                                    (row['CAS Number'], row['EC'], row['Fórmula Molecular'], 
                                     row['HAZ Classificação'], row['Sobre 1'], row['Sobre 2'], 
                                     row['Uso Consumidor'])
                                )

                conn.commit()
                flash("Dados armazenados com sucesso!", "success")

            except Exception as e:
                conn.rollback()
                flash(f"Erro ao salvar no banco de dados: {e}", "danger")

            finally:
                cursor.close()
                conn.close()

            results = {cas: {db_name: data.to_html(classes='table table-striped') for db_name, data in dbs.items()} for cas, dbs in df_results.items()}

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)