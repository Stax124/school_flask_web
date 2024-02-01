from flask import Flask, render_template, request, redirect, url_for, session, Markup, flash
import functools

from sqlitewrap import SQLite

from werkzeug.security import generate_password_hash, check_password_hash

from sqlite3 import IntegrityError

import datetime


# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b"totoj e zceLa n@@@hodny retezec nejlep os.urandom(24)"
app.secret_key = b"x6\x87j@\xd3\x88\x0e8\xe8pM\x13\r\xafa\x8b\xdbp\x8a\x1f\xd41\xb8"

def prihlasit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login", url=request.path))

    return wrapper

@app.route("/", methods=["GET"])
def index():
    return render_template("base.html")

@app.route("/prsten/")
def prsten():
    return render_template("prsten.html")

@app.route("/retizek/")
def retizek():
    return render_template("retizek.html")


@app.route("/naramek/")
def naramek():
    return render_template("naramek.html")


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login/", methods=["POST"])
def login_post():
    jmeno=request.form.get('jmeno','')
    heslo=request.form.get('heslo','')
    url = request.args.get("url", "")  #url je obsažena v adrese, proto request args
    with SQLite('data.sqlite') as cursor:
        response = cursor.execute("SELECT login, password FROM user WHERE login = ?", [jmeno])
        response = response.fetchone()
        if response:
            login, password = response
            if check_password_hash(password, heslo):
                session["user"] = jmeno
                flash("Jsi přihlášen!", "success")
                if url: 
                    return redirect(url)
                else: 
                    return redirect(url_for("prsten"))
            else:
                flash("Nesprávné přihlašovací údaje!", "error")
        else:
            flash("Nesprávné přihlašovací údaje!", "error")
        return redirect(url_for("login",url=url))

@app.route("/logout/")
def logout():
    session.pop("user",None)
    flash("Byl jsi odhlášen!", "success")
    return redirect(url_for("index"))

@app.route("/vzkazy/", methods=["GET"])
def vzkazy():
    if 'user' not in session:
        flash("Tato stránka je pouze pro příhlašné!", "error")
        return redirect(url_for("login", url=request.path))
    
    with SQLite("data.sqlite") as cursor:
        response=cursor.execute("SELECT login, body, datetime, message.id FROM user JOIN message ON user.id = message.user_id ORDER BY datetime DESC")
        response=list(response.fetchall())
        print(response)



    return render_template("vzkazy.html", response=response, d=datetime.datetime)

    
@app.route("/vzkazy/", methods=["POST"])
def vzkazy_post():
    if 'user' not in session:
        flash("Tato stránka je pouze pro příhlašné!", "error")
        return redirect(url_for("login", url=request.path)) 

    with SQLite('data.sqlite') as cursor:
        response= cursor.execute("SELECT id FROM user WHERE login=?", [session["user"]])
        response= response.fetchone()
        user_id=list(response)[0]

    vzkaz = request.form.get("vzkaz")
    print(f"Vzkaz: {vzkaz}")
    if vzkaz:
        with SQLite('data.sqlite') as cursor:
            cursor.execute("INSERT INTO message (user_id, body, datetime) VALUES (?,?,?)", [user_id, vzkaz, datetime.datetime.now()])  
    return redirect(url_for("vzkazy"))

@app.route("/registration/", methods=["GET"])
def registration():
    return render_template("registration.html")

@app.route("/registration/", methods=["POST"])
def registration_post():
    jmeno = request.form.get("jmeno", "")
    heslo1  =  request.form.get("heslo1", "")
    heslo2 =  request.form.get("heslo2", "")
    if len(jmeno)<5:
        flash("Heslo je menši než 5 znaků!", "error")
    if len(heslo1)<5:
        flash("Heslo je menši než 5 znaků!", "error")
    if heslo1!=heslo2:
        flash("Musíte zadat dvakrát stejné heslo", "error")
        return redirect(url_for("registration"))
    hash_ = (generate_password_hash(heslo1))
    try:
        with SQLite('data.sqlite') as cursor:
            cursor.execute('INSERT INTO user(login,password) VALUES(?,?)', [jmeno, hash_])
        flash(f"Uživatel `{jmeno}` byl přidán!", "success")
    except IntegrityError:
        flash(f"Uživatel již existuje!", "error")

    return redirect(url_for("registration"))