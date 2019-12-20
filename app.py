import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from random_password import random_password
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/Users/labieno/PycharmProjects/untitled/static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
# config for the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# app.config["MONGO_URI"] = "mongodb://localhost:27017/db-noigual"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///noigual.sqlite3'
# mongo = PyMongo(app)
db = SQLAlchemy(app)
app.secret_key = b'_52ksaLFwerWWrcdesal'

app.config['MAIL_SERVER'] = 'out.virgilio.it'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lubrano.biagio@virgilio.it'
app.config['MAIL_PASSWORD'] = 'prova'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# DB models###############

# utenti-------------
class Utenti(db.Model):
    email = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)
    poteri = db.Column(db.Integer, nullable=False, default=0)
    ordini = db.relationship('Ordini', backref='utente', lazy=True)


def __init__(self, email, password, poteri):
    self.email = email
    self.password = password
    self.poteri = poteri


# gioielli------------
class Gioielli(db.Model):
    brand = db.Column(db.String(30), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    immagine = db.Column(db.String(50), nullable=False, default='140X140.gif')
    prezzo = db.Column(db.Float, nullable=False)
    codice = db.Column(db.String(30), primary_key=True)


def __init__(self, unicode, brand, categoria, immagine, prezzo, codice, ordine):
    self.unicode = unicode
    self.brand = brand
    self.categoria = categoria
    self.immagine = immagine
    self.prezzo = prezzo
    self.codice = codice
    self.ordine = ordine


# -------------------------


# ordini------------
class Ordini(db.Model):
    author = db.Column(db.String(30), db.ForeignKey('utenti.email'), nullable=False)
    codice = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    totale = db.Column(db.Float, unique=True, nullable=False)
    cliente = db.Column(db.String(), db.ForeignKey('clienti.codice_fiscale'), nullable=False)
    pagamento = db.Column(db.String(20), nullable=False)
    carrello = db.relationship('Gioielli_Ordinati', backref='ordine', lazy=True)


def __init__(self, author, data, totale, cliente, pagamento, carrello):
    self.author = author
    self.data = data
    self.totale = totale
    self.cliente = cliente
    self.pagamento = pagamento
    self.carrello = carrello


# -------------------------
# gioielli ordinati------------
class Gioielli_Ordinati(db.Model):
    unicode = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(30), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    immagine = db.Column(db.String(50), nullable=False, default='140X140.gif')
    prezzo = db.Column(db.Float, nullable=False)
    codice = db.Column(db.String(30), db.ForeignKey('gioielli.codice'), nullable=False)
    codice_ordine = db.Column(db.Integer, db.ForeignKey('ordini.codice'), nullable=False)


def __init__(self, brand, categoria, immagine, prezzo, codice, codice_ordine):
    self.brand = brand
    self.categoria = categoria
    self.immagine = immagine
    self.prezzo = prezzo
    self.codice = codice
    self.codice_ordine = codice_ordine


# -------------------------


# clienti------------
class Clienti(db.Model):
    nome = db.Column(db.String(10), nullable=False)
    cognnome = db.Column(db.String(15), nullable=False)
    via = db.Column(db.String(30), nullable=False)
    cap = db.Column(db.Integer, nullable=False)
    citta = db.Column(db.String(20), nullable=False)
    provincia = db.Column(db.String(4), nullable=False)
    partita_iva = db.Column(db.String(30), nullable=False, unique=True)
    codice_fiscale = db.Column(db.String(40), primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    banca = db.Column(db.String(30), nullable=False)
    iban = db.Column(db.String(30), nullable=False)
    ragione_sociale = db.Column(db.String(40), nullable=False, unique=True)
    ordini = db.relationship('Ordini', backref='cliente', lazy=True)


def __init__(self, nome, cognome, via, cap, citta, provincia, partita_iva, codice_fiscale, email, banca, iban,
             ragione_sociale, ordini):
    self.nome = nome
    self.cognome = cognome
    self.via = via
    self.cap = cap
    self.citta = citta
    self.provincia = provincia
    self.partita_iva = partita_iva
    self.codice_fiscale = codice_fiscale
    self.email = email
    self.banca = banca
    self.iban = iban
    self.ragione_sociale = ragione_sociale
    self.ordini = ordini


# -------------------------


#########################



app.host = '0.0.0.0'

# global orders index
# indice_ordini = 0
# global clients code
codice_clienti = 0
# nomifile global
nomi_file = []

# global spesa
spesa = 0.0

# global brand in visualizzazione
brand_attuale = "none"

# carrello
carrello = []

# quantity
quantity = []

# global per routing
frase = "null"
back_to = "null"


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/routing', methods=["POST", "GET"])
def routing():
    global indice_ordini
    try:
        # lista di brand
        gioielli = Gioielli.query.all()
        nomi_brand = []
        for i in gioielli:
            nomi_brand.append(i.brand)

        # lista di clienti
        customers = Clienti.query.all()
        arrayclienti = []
        for x in customers:
            arrayclienti.append(x.ragione_sociale)

        # lista ordini se admin tutto se agent --> partial
        if session["type"] == "admin":
            orders = Ordini.query.all()
        else:
            orders = Ordini.query.filter_by(author=session["username"]).all()

        ordini = []
        for i in orders:
            ordini.append(i)

        ordini.reverse()

    # if ordini:
    #   indice_ordini = int(ordini[0].codice)
    # else:
    #      indice_ordini = 0

    except:
        print("-- erorre in fetchin data ---")
    try:
        errore = "nessuno"

        if request.form["value"] == "clienti":
            errore = "in clienti"
            return render_template("clienti.html", clienti=arrayclienti)

        elif request.form["value"] == "aggiungi_cliente" :
            return render_template("crea_cliente.html")
        elif request.form["value"] == "rimuovi_cliente":
            return render_template("elimina_cliente.html", clienti=arrayclienti)

        elif request.form["value"] == "ordini" :
            errore = "in ordini"
            return render_template("ordini.html", ordini=ordini)

        elif request.form["value"] == "espositore":
            # effettuare distinzione admin agemnt
            return render_template("manage_admin.html", nomi_brand=nomi_brand)

        elif request.form["value"] == "account":
            return render_template("account.html")

        elif request.form["value"] == "upload":
            return render_template("upload.html")
        #modifica ordine
        elif request.form["value"] == "modifica_ordine":
            return render_template("modify-order.html")
        #crea ordine
        elif request.form["value"] == "crea_ordine":

            return render_template("crea_ordine.html", clienti=arrayclienti, carrello=carrello, totale=spesa)
        print("non trova nessun route da soddisfare in function routing")


    except:
        global frase
        print("none value")

        if frase == "null" and session["username"]:
            frase = "Benvenuto " + session["username"]
        elif session["username"] == "" or session["username"] == None :
            render_template("home.html")

    return render_template("welcome.html", frase=frase, back_to=back_to)


def sending_email(destinatario):
    token = random_password(length=6,
                            characters=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'M', 'a', 'b', 'c', 'd', 'e',
                                        'f'
                                , 'g', 'h', 'i', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't'
                                , 'u', 'v', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    msg = Message('Accesso credenziali', sender='No Igual gioielli', recipients=destinatario)
    msg.body = f"ciao  {destinatario} , conserva queste informazioni accuratamente,ti abbiamo appena inviato le credenziali di accesso per l'espositore online di No Igual gioielli, questa è la tua password --> {token} <--  "
    print(msg)
    try:
        mail.send(msg)
    except:
        print("message password not sent")
        return "errore"
    return token

@app.route('/logging', methods=["POST"])
def logging():  # admin/admin   agent/123     agent2/123
    username = request.form["username"]
    password = request.form["password"]

    # ricerca utente in DB
    cursore = Utenti.query.filter_by(email=username).first()

    if cursore == None:
        errore = "utente non  registrato"
        return render_template('home.html', error_name=errore)

    else:
        if check_password_hash(cursore.password, password):
            if cursore.poteri == 1:
                tipo_utente = "admin"
                session["type"] = "admin"
                session["username"] = request.form["username"]
                return redirect(url_for("routing"))  # call the method home to load fresh data on access

            else:
                tipo_utente = "rappresentante"
                session["type"] = "agent"
                session["username"] = request.form["username"]
                return redirect(url_for("routing"))  # call the method home to load fresh data on access
        else:
            errore = "password errata"
            return url_for("index", error_pass=errore)


@app.route('/create_credentials', methods=["POST"])
def create_credentials():  #function per creare credenziali da pannello ADMIN
    global frase, back_to
    #crea utente
    if request.form["tipo-azione"] == "nuovo-utente":
        try:
            password_generata = sending_email(request.form["email"])
            if password_generata == "errore":
                frase = "errore nell'invio del messaggio password email"
                back_to = "account"
                return redirect(url_for("routing"))
            new_utente = Utenti(request.form["email"], password_generata)
            db.session.add(new_utente)
            db.session.commit()

        except:
            frase = "errore nella creazione nuovo utente"
            back_to = "account"
            return redirect(url_for("routing"))
        frase = "creazione avvenuta con successo"
        back_to = "account"
        return redirect(url_for("routing"))
    #aggiorna password utente
    else:
        try:
            password_generata = sending_email(request.form["email"])
            if password_generata == "errore":
                frase = "errore nell'invio del messaggio password email"
                back_to = "account"
                return redirect(url_for("routing"))
            else:
                user = Utenti.query.filter_by(request.form["email"]).first()
                user.password = password_generata
                db.session.commit()
        except:
            frase = "errore nella modifica utente"
            back_to = "account"
            return redirect(url_for("routing"))
        frase = "modifica avvenuta con successo"
        back_to = "account"
        return redirect(url_for("routing"))


@app.route('/switch_modifica_crea', methods=["POST"])
def switch_modifica_crea():
    if request.form["value"] == "new-utente":
        return ' <h4>Inserisci nuova email</h4> <input class="dritto" type="email" name="email" value="inserisci email">' + '<p>La password sarà generata automaticamente<br> e inviata via email</p>' + '<input class="dritto" type="submit" value="Procedi">'
    else:
        return '<h4 class="dritto">Inserisci vecchia email</h4><input class="dritto " type="email" name="vecchia-email" value="inserisci email"><h4>Inserisci nuova email</h4><input class="dritto" type="email" name="email" value="inserisci email"><p>La password sarà generata automaticamente<br> e inviata via email</p><input class="dritto" type="submit" value="Procedi">'






@app.route('/adding_orders', methods=["POST"])
def adding_orders():
    global carrello
    global spesa
    global indice_ordini
    if request.form["tipo"] == "update":
        try:
            result = Ordini.query.filter_by(codice=request.form["ordine_numero"]).first()
            cliente = Clienti.query.filter_by(ragione_sociale=request.form["ragione_sociale"]).first()
            result.pagamento = request.form["pagamento"]
            result.data = request.form["data"]
            result.cliente = cliente.codice_fiscale

            # non effettua update del carrello ma solo dati dal form
            # ma si potrebbe fare inserendo roba nel carrello e poi aggiornando l'ordine
            # da qui tramite modifica

            print(result)
            return redirect(url_for("home"))
        except:
            print("update failed")
    else:
        # altrimenti è una nuova creazione col tasto crea ordini dando per scontato che il carrello
        # sia pieno!

        try:
            cliente = Clienti.query.filter_by(request.form["ragione_sociale"]).first()
            ordine = Ordini(session["username"], request.form["data"], spesa, cliente.codice_fiscale,
                            request.form["pagamento"])
            mongo.db.ordini.insert(
                {"ordine_numero": f"{indice_ordini}", "codice_cliente": "prova",
                 "ragione_sociale": request.form["ragione_sociale"],
                 "pagamento": request.form["pagamento"], "carrello": carrello, "data": request.form["data"],
                 "agent_code": session["username"]})
            error = 0

        except:
            error = 1

        carrello.clear()
        spesa=0
        print(error)
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
    global frase, back_to
    frase = "ordine effettuato con successo"
    back_to = "ordini"
    if session["type"] == "admin":

        return redirect(url_for("routing"))
    else:
        return redirect(url_for("routing"))


@app.route('/modifica_ordine', methods=["POST"])
def modifica_ordine():
    print("modifica")
    cursore = mongo.db.ordini.find_one({"ordine_numero": request.form["value"]})
    return render_template("modify-order.html", ordine=cursore)


@app.route('/elimina_ordine', methods=['POST'])
def elimina_ordine():
    global indice_ordini

    try:

        mongo.db.ordini.delete_one({"ordine_numero": request.form["value"]})
        indice_ordini = indice_ordini - 1
        cursore = mongo.db.ordini.find()
    except:
        print("errore in deleting ")

    return render_template("ordini.html", ordini=cursore)


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
    return render_template("welcome.html", frase="Cliente aggiunto", back_to="clienti")


# rimozione cliente nel db
@app.route('/removing_customer', methods=['POST'])
def removing_customer():
    global codice_clienti
    mongo.db.clienti.delete_one({
        "ragione_sociale": request.form["cliente-da-eliminare"]
    })
    return render_template("welcome.html", frase="Cliente rimosso", back_to="clienti")




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_info', methods=['POST'])
def upload_info_file():
    try:
        brand_cursore = mongo.db.brand.find({"brand": request.form["brand"]})
    except:
        print("brand  non trovato")

    espositore = []
    categorie = []
    iteratore = []
    # preparo dati in un vettore da inserire in DB
    for i in nomi_file:
        espo = {"immagine": i,
                "codice": request.form[f"codice_id{i}"],
                "prezzo": request.form[f"prezzo{i}"]}
        espositore.append(espo.copy())
        espo.clear()

    t = 0

    for i in brand_cursore:
        t = t + 1
    # la collezione brand ha un campo stringa brand
    # un campo categorie che è un vettore con tutti i nomi degli album
    #e un campo espositore che ha il campo con nome categoria ed è un vettore con tutte le info sui file

    if t == 0:
        print("insert")
        categorie.append(f"{request.form['album']}")

        mongo.db.brand.insert({
            "brand": request.form["brand"],
            "categorie": categorie,
            f"{request.form['album']}": espositore
        })
    else:

        # ci sono due casi di update
        # primo in cui il brand esiste già ma si sta creando una nuova categoria
        #secondo in cui la categoria anche esiste già e si vuole aggiungere/ sostituire elementi

        print("update")

        # caso in cui esiste brand e anche categoria
        try:
            print(brand_cursore)

        except:
            print("errore in fetching the album, so it doesnt exist already")


        mongo.db.brand.update_one({"brand": request.form["brand"]},
                                  {"$set": {"categorie": categorie,
                                            f"{request.form['album']}": espositore}})

    return redirect(url_for("routing"))


@app.route('/uploading', methods=['POST'])
def upload_file():
    nomi_file.clear()  #pulisco array per evitare sovrapposizioni in upload successivi
    if request.method == 'POST' :

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
    return render_template("welcome.html", frase="Errore in upload file")


@app.route("/espositore", methods=["POST", "GET"])
def mostra_espositore():
    global brand_attuale

    brand_attuale = request.form["value"]
    brand = mongo.db.brand.find({"brand": request.form["value"]})
    return render_template("album.html", album=brand)


@app.route("/view_img", methods=["POST", "GET"])
def view_img():
    global brand_attuale
    return render_template("view_img.html", url_foto=request.form["value"], brand_attuale=brand_attuale)

@app.route("/add_to_cart", methods=["POST", "GET"])
def add_to_cart():
    global carrello
    global spesa
    global quantity

    # dati diviene un array
    dati = request.form["data"].split(",")
    carrello.append(dati[0])
    quantity.append(dati[1])

    prezzo = float(dati[2]) * (float(dati[1]))
    spesa = float("{0:.2f}".format(spesa + prezzo))
    print(spesa)
    return f"{spesa}"

@app.route("/remove_from_cart", methods=["POST", "GET"])
def remove_from_cart():
    global carrello
    global spesa
    global quantity

    # splitto la stringa in due  e assegno ad codice e prezzo
    stringa = request.form["data"].split(",")

    codice = stringa[0]
    prezzo = float(stringa[2])

    if spesa > 0 :
        for i in range(0, len(carrello)):
            if carrello[i] == codice:
                prezzo_finale = float(quantity[i]) * prezzo
                quantity.pop(i)
                break
    if carrello[i] == codice:
        carrello.remove(codice)
        spesa = round(float(spesa - prezzo_finale),2)

    return f"{spesa}"




if __name__ == '__main__':
    app.run()
