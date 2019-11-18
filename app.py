import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/Users/labieno/PycharmProjects/untitled/static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
# config for the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["MONGO_URI"] = "mongodb://localhost:27017/db-noigual"
mongo = PyMongo(app)
app.secret_key = b'_52ksaLFwerWWrcdesal'

app.debug = True

app.host = '0.0.0.0'

# global orders index
indice_ordini = 0
# global clients code
codice_clienti = 0
# nomifile global
nomi_file = []


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/logging', methods=["POST"])
def logging():  # admin/admin   agent/123     agent2/123
    username = request.form["username"]
    password = request.form["password"]

    cursore = mongo.db.utenti.find_one({'username': username})

    if cursore == None:
        errore = "utente non  registrato"
        # ELIMINARE RIGA BELOW
        # mongo.db.utenti.insert({"username": username, "password": generate_password_hash(password), "admin": "yes"})
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
    if request.form["tipo"] == "update":
        try:
            result = mongo.db.utenti.update_one({"ordine_numero": request.form["ordine_numero"]},
                                                {"$set": {"ragione_sociale": request.form["ragione_sociale"],
                                                          "pagamento": request.form["pagamento"],
                                                          "data": request.form["data"],
                                                          "agent_code": session["username"]}})
            print(result)
            return redirect(url_for("home"))
        except:
            print("update failed")
    else:
        if indice_ordini == 0:
            ordine_numero = 1
            indice_ordini = indice_ordini + 1
        else:
            ordine_numero = indice_ordini + 1
            indice_ordini = indice_ordini + 1

        try:
            mongo.db.ordini.insert(
                {"ordine_numero": f"{indice_ordini}", "codice_cliente": "prova",
                 "ragione_sociale": request.form["ragione_sociale"],
                 "pagamento": request.form["pagamento"], "data": request.form["data"],
                 "agent_code": session["username"]})
            error = 0

        except:
            error = 1

        print(error)
    if session["type"] == "admin":
        return redirect(url_for("home"))  # call the method home to load fresh data on access
    else:
        return redirect(url_for("home"))  # call the method home to load fresh data on access


@app.route('/modifica_ordine', methods=["POST"])
def modifica_ordine():
    print("modifica")
    cursore = mongo.db.ordini.find_one({"ordine_numero": request.form["ordine_numero"]})
    return render_template("modify-order.html", ordine=cursore)


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


# aggiunta cliente nel db
@app.route('/adding_customer', methods=['POST'])
def adding_customer():
    global codice_clienti
    mongo.db.clienti.insert({
        "nome": request.form["nome"],
        "cognome": request.form["cognome"],
        "ragione_sociale": request.form["ragione_sociale"],
        "via": request.form["via"],
        "cap": request.form["cap"],
        "città": request.form["città"],
        "provincia": request.form["provincia"],
        "partita_iva": request.form["partita_iva"],
        "codice_fiscale": request.form["codice_fiscale"],
        "codice_sdi": request.form["codice_sdi"],
        "email": request.form["email"],
        "telefono": request.form["telefono"],
        "banca": request.form["banca"],
        "iban": request.form["iban"]
    })
    return redirect(url_for('home'))


# this method return the homepage with all the refreshed data from DB
@app.route('/home')
def home():
    global indice_ordini
    try:
        # dictionary per i clienti
        brand = mongo.db.brand.find()
        nomi_brand = []
        for i in brand:
            nomi_brand.append(i)
        clienti = mongo.db.clienti.find().sort("ragione_sociale", 1)
        arrayclienti = []
        for x in clienti:
            arrayclienti.append(x)

        # ottengo cursore da mongo se admin tutti ordini
        # se agent solo ordini effettuati
        if session["type"] == "admin":
            cursore = mongo.db.ordini.find()
        else:
            cursore = mongo.db.ordini.find({"agent_code": session["username"]})

        ordini = []
        for i in cursore:
            ordini.append(i)

        ordini.reverse()

        if ordini:
            indice_ordini = int(ordini[0]["ordine_numero"])
        else:
            indice_ordini = 0

    except:
        print("--erorre in home---")
    if session["type"] == "admin":
        return render_template("manage_admin.html", ordini=ordini, clienti=arrayclienti, nomi_brand=nomi_brand)
    else:
        return render_template("manage_agent.html", ordini=ordini, clienti=arrayclienti, nomi_brand=nomi_brand)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_info', methods=['POST'])
def upload_info_file():
    brand_cursore = mongo.db.brand.find({"brand": request.form["brand"]})

    espositore = []
    categorie = []
    # ciclo for to create array espositore and dictionary within inside
    for i in nomi_file:
        espo = {"immagine": i,
                "codice": request.form[f"codice_id{i}"],
                "prezzo": request.form[f"prezzo{i}"]}
        espositore.append(espo.copy())
        espo.clear()

    t = 0

    for i in brand_cursore:
        t = t + 1

    if t == 0:
        print("insert")
        categorie.append(f"{request.form['album']}")

        mongo.db.brand.insert({
            "brand": request.form["brand"],
            "categorie": categorie,
            f"{request.form['album']}": espositore
        })
    else:
        print("update")
        brand_cursore = mongo.db.brand.find({"brand": request.form["brand"]})
        for i in brand_cursore:
            print(i)

        # qui problema con cursore pymongo????

        mongo.db.brand.update_one({"brand": request.form["brand"]},
                                  {"$set": {"categorie": categorie,
                                            f"{request.form['album']}": espositore}})

    return redirect(url_for("home"))


@app.route('/uploading', methods=['POST'])
def upload_file():
    nomi_file.clear()  #pulisco array per evitare sovrapposizioni in upload successivi
    if request.method == 'POST':

        file = request.files.getlist("file")

        for i in file:
            nomi_file.append(i.filename)


        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        # if user does not select file, browser also
        # submit an empty part without filename
        for x in file:
            if x.filename == '':
                flash('No selected file')
                return redirect(request.url)

        # qui loop for per save multiple files
        for t in file:
            if t and allowed_file(t.filename):
                filename = secure_filename(t.filename)
                t.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template("upload.html", nomi_file=nomi_file,
                               album=request.form["album"], brand=request.form["brand"])
    return "<h1>errore in upload del file</h1>"


@app.route("/espositore", methods=["POST", "GET"])
def mostra_espositore():
    brand = mongo.db.brand.find({"brand": request.form["value"]})
    return render_template("album.html", album=brand)


@app.route("/view_img", methods=["POST", "GET"])
def view_img():
    return render_template("view_img.html", url_foto=request.form["value"])


if __name__ == '__main__':
    app.run()
