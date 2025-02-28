import os
import uuid

import resend
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from src import app, bcrypt, db
from src.database import connection_db
from src.extractors.extractor import extract_data
from src.forms import LoginForm, RecoveryPassword, RecoveryPasswordForm, RegisterForm
from src.models import TokensPassword, Users

load_dotenv()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users(
            name=form.name.data, email=form.email.data, password_cryp=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("articles_extractor"))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f"Error user register {err}", category="danger")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_logged = Users.query.filter_by(email=form.email.data).first()
        if user_logged and user_logged.convert_password(
            password_clean_text=form.password.data
        ):
            login_user(user_logged)
            flash(
                f"Success! You're logged in as: {user_logged.name}", category="success"
            )
            return redirect(url_for("articles_extractor"))
        else:
            flash(f"Wrong email or password. Try again!", category="danger")
    return render_template("login.html", form=form)


@app.route("/toxins_finder", methods=["GET", "POST"])
def toxins_finder():
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
                                    (
                                        row["CAS Number"],
                                        row["CID"],
                                        row["Fórmula Molecular"],
                                        row["Sinônimos"],
                                        row["Peso Molecular"],
                                        row["Datas"],
                                        row["Descrição"],
                                    ),
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
                                    (
                                        row["CAS Number"],
                                        row["EC"],
                                        row["Fórmula Molecular"],
                                        row["HAZ Classificação"],
                                        row["Sobre 1"],
                                        row["Sobre 2"],
                                        row["Uso Consumidor"],
                                    ),
                                )

                conn.commit()
                flash("Dados armazenados com sucesso!", "success")

            except Exception as e:
                conn.rollback()
                flash(f"Erro ao salvar no banco de dados: {e}", "danger")

            finally:
                cursor.close()
                conn.close()

            results = {
                cas: {
                    db_name: data.to_html(classes="table table-striped")
                    for db_name, data in dbs.items()
                }
                for cas, dbs in df_results.items()
            }

    return render_template("toxins_finder.html", results=results)


@app.route("/recovery_password_form", methods=["GET", "POST"])
def recovery_passwordForm():
    form = RecoveryPasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            uuid_id = str(uuid.uuid1().hex)
            token_password = TokensPassword(
                user_id=user.id,
                token=uuid_id,
                # ajustar
                link=f"localhost:5000/recovery_password/{user.id}/{uuid_id}",
            )
            db.session.add(token_password)
            db.session.commit()

            resend.api_key = os.getenv("RESEND")
            resend.Emails.send(
                {
                    "from": "onboarding@resend.dev",
                    "to": f"{form.email.data}",
                    "subject": "Recovery Password",
                    "html": f"<b>Hello, "
                    + f"Click here to reset your password {token_password.link}</b><br><br>"
                    + "If you habe any questions, contact us "
                    + "bambuenterprise@gmail.com",
                }
            )

            flash(
                f"Success! Your password recovery request was sent to your email: {form.email.data}",
                category="success",
            )
            return redirect(url_for("login"))
        else:
            flash(f"Account not found, please review your e-mail", category="danger")
    return render_template("recovery_password_form.html", form=form)


@app.route("/recovery_password/<id>/<token>", methods=["GET", "POST"])
def recovery_password(token, id):
    form = RecoveryPassword()
    token_password = TokensPassword.query.filter_by(token=token).first()
    if token_password:
        user = Users.query.filter_by(id=id).first()
        if user and form.validate_on_submit():
            user.password = bcrypt.hashpw(
                form.password.data.encode("utf-8"), bcrypt.gensalt()
            )
            flash(
                f"{user.name}, your password has been changed successfuly",
                category="success",
            )
            db.session.delete(token_password)
            db.session.commit()
            return redirect(url_for("login"))
    else:
        flash(f"Token expired, generate another token", category="danger")
        return redirect(url_for("recovery_passwordForm"))
    return render_template("recovery_password.html", form=form, token=token, id=id)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully", category="info")
    return redirect(url_for("home"))
