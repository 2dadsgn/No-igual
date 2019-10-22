from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/db-noigual"
mongo = PyMongo(app)
app.secret_key = b'_52ksaLFwerWWrcdesal'

# global orders index
indice_ordini = 0

@app.route('/')
def index():
    return render_template("home.html")


@app.route('/logging', methods=["POST"])
def logging():  #admin/admin   agent/123     agent2/123
    username = request.form["username"]
    password = request.form["password"]

    cursore = mongo.db.utenti.find_one({'username': username})

    if cursore == None:
        errore = "utente non  registrato"
        # ELIMINARE RIGA BELOW
        mongo.db.utenti.insert({"username": username, "password": generate_password_hash(password), "admin": "no"})
        return render_template('home.html', error_name=errore)

    else:
        if check_password_hash(cursore["password"], password):
            if cursore["admin"] == "yes":
                tipo_utente = "admin"
                session["type"] = "admin"
                session["username"] = request.form["username"]
                return redirect(url_for("home"))  # call the method home to load fresh data on access

            else:
                tipo_utente = "rappresentante"
                session["type"] = "agent"
                session["username"] = request.form["username"]
                return redirect(url_for("home"))  # call the method home to load fresh data on access
        else:
            errore = "password errata"
            return url_for("index", error_pass=errore)


@app.route('/adding_orders', methods=["POST"])
def adding_orders():
    global indice_ordini
    if indice_ordini == 0:
        ordine_numero = 1
        indice_ordini = indice_ordini + 1
    else:
        ordine_numero = indice_ordini + 1
        indice_ordini = indice_ordini+1
    try:
        mongo.db.ordini.insert(
            {"ordine_numero": f"{indice_ordini}", "codice_cliente": request.form["codice_cliente"],
             "pagamento": request.form["pagamento"], "data": request.form["data"],
             "agent_code": session["username"]})
        error = 0
    except:
        error = 1

    if session["type"] == "admin":
        return redirect(url_for("home"))  # call the method home to load fresh data on access
    else:
        return redirect(url_for("home"))  # call the method home to load fresh data on access


@app.route('/modifica_ordine', methods=["POST", "GET"])
def modifica_ordine():
    print("modifica")
    return render_template("home.html")


@app.route('/elimina_ordine', methods=['POST'])
def elimina_ordine():
    global indice_ordini

    try:
        # print del numero ordine, eliminazione dal DB e decremento variabile globale
        print(request.form["ordine_numero"])
        mongo.db.ordini.delete_one({"ordine_numero": request.form["ordine_numero"]})
        indice_ordini = indice_ordini - 1
    except:
        print("errore in deleting ")

    return redirect(url_for('home'))



# this method return the homepage with all the refreshed data from DB
@app.route('/home')
def home():
    global indice_ordini
    try:
        # ottengo cursore da mongo se admin tutti ordini
        # se agent solo ordini effettuati
        if session["type"] == "admin":
            cursore = mongo.db.ordini.find()
        else:
            cursore = mongo.db.ordini.find({"agent_code": session["username"]})

        ordine = []
        ordini = []
        # itero cursore per ogni riga nel DB e alla fine avrò le singole
        # righe in ogni cella
        for i in cursore:
            ordine.append(i["ordine_numero"])
            ordine.append(i["codice_cliente"])
            ordine.append(i["pagamento"])
            ordine.append(i["data"])  #mancano codici articoli con totale
            ordini.append(ordine.copy())
            ordine.clear()
        ordini.reverse()
        indice_ordini = int(ordini[0][0])

    except:
        print("--erorre in home---")
    if session["type"] == "admin":
        return render_template("manage_admin.html", ordini=ordini)
    else:
        return render_template("manage_agent.html", ordini=ordini)


if __name__ == '__main__':
    app.run()
