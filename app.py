from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/db-noigual"
mongo = PyMongo(app)
app.secret_key = b'_52ksaLFwerWWrcdesal'


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/logging', methods=["POST"])
def logging():
    username = request.form["username"]
    password = request.form["password"]

    cursore = mongo.db.utenti.find_one({'username': username})

    if cursore == None:
        errore = "utente non  registrato"
        # mongo.db.utenti.insert({"username": username, "password": generate_password_hash(password), "admin": "no"})
        return render_template('home.html', error_name=errore)

    else:
        if check_password_hash(cursore["password"], password):
            if cursore["admin"] == "yes":
                tipo_utente = "admin"
                session["type"] = "admin"
                return redirect(url_for("home"))  # call the method home to load fresh data on access

            else:
                tipo_utente = "rappresentante"
                session["type"] = "agent"
                return redirect(url_for("home"))  # call the method home to load fresh data on access
        else:
            errore = "password errata"
            return url_for("index", error_pass=errore)


@app.route('/adding_orders', methods=["POST"])
def adding_orders():
    try:
        mongo.db.ordini.insert(
            {"ordine_numero": request.form["ordine_numero"], "cognome_cliente": request.form["cognome_cliente"],
             "nome_cliente": request.form["nome_cliente"], "data": request.form["data"],
             "agent_code": session["username"]})
        error = 0
    except:
        error = 1

    if session["type"] == "admin":
        return redirect(url_for("home"))  # call the method home to load fresh data on access
    else:
        return redirect(url_for("home"))  # call the method home to load fresh data on access


# this method return the homepage with all the refreshed data from DB
@app.route('/home')
def home():
    try:
        # ottengo cursore da mongo
        cursore = mongo.db.ordini.find()
        ordine = []
        ordini = []
        # itero cursore per ogni riga nel DB e alla fine avrò le singole
        # righe in ogni cella
        for i in cursore:
            ordine.append(i["ordine_numero"])
            ordine.append(i["nome_cliente"])
            ordine.append(i["cognome_cliente"])
            ordine.append(i["data"])
            ordini.append(ordine.copy())
            ordine.clear()
        ordini.reverse()

    except:
        print("--erorre in home---")
    if session["type"] == "admin":
        return render_template("manage_admin.html", ordini=ordini)
    else:
        return render_template("manage_agent.html", ordini=ordini)


if __name__ == '__main__':
    app.run()
