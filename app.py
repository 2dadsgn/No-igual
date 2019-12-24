import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from random_password import random_password
from werkzeug.security import check_password_hash, generate_password_hash
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
    brand = db.Column(db.String(30), db.ForeignKey('brand.nome'), nullable=False)
    categoria = db.Column(db.String(20), db.ForeignKey('categorie.unicode'))
    immagine = db.Column(db.String(50), nullable=False, default='140X140.gif')
    prezzo = db.Column(db.Float, nullable=False)
    codice = db.Column(db.String(30), primary_key=True)

    def __init__(self, brand, categoria, immagine, prezzo, codice):
        self.brand = brand
        self.categoria = categoria
        self.immagine = immagine
        self.prezzo = prezzo
        self.codice = codice
# -------------------------

# ---------BRAND----------
class Brand(db.Model):
    nome = db.Column(db.String(20), primary_key=True)
    img = db.Column(db.String(30), nullable=True, default='140X140.gif')
    categorie = db.relationship('Categorie', backref='marca', lazy=True)
    oggetto = db.relationship('Gioielli', backref='marca', lazy=True)

    def __init__(self, nome):
        self.nome = nome


# --------------------


# ---------categorie----------
class Categorie(db.Model):
    unicode = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)
    brand = db.Column(db.String(30), db.ForeignKey('brand.nome'), nullable=False)
    gioielli = db.relationship('Gioielli', backref='categ', lazy=True)

    def __init__(self, nome, brand):
        self.nome = nome
        self.brand = brand



# ordini------------
class Ordini(db.Model):
    author = db.Column(db.String(30), db.ForeignKey('utenti.email'), nullable=False)
    codice = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    totale = db.Column(db.Float, unique=True, nullable=False)
    cliente = db.Column(db.String(), db.ForeignKey('clienti.codice_fiscale'), nullable=False)
    pagamento = db.Column(db.String(20), nullable=False)
    carrello = db.relationship('Gioielli_Ordinati', backref='ordine', lazy=True)

    def __init__(self, author, data, totale, cliente, pagamento):
        self.author = author
        self.data = data
        self.totale = totale
        self.cliente = cliente
        self.pagamento = pagamento


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

    def __init__(self, unicode, brand, categoria, immagine, prezzo, codice, codice_ordine):
        self.unicode = unicode
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
    codice_sdi = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    banca = db.Column(db.String(30), nullable=False)
    iban = db.Column(db.String(30), nullable=False)
    ragione_sociale = db.Column(db.String(40), nullable=False, unique=True)
    ordini = db.relationship('Ordini', backref='ordinato_da', lazy=True)

    def __init__(self, nome, cognome, via, cap, citta, provincia, partita_iva, codice_fiscale, email, codice_sdi,
                 telefono, banca, iban, ragione_sociale):
        self.nome = nome
        self.cognome = cognome
        self.via = via
        self.cap = cap
        self.citta = citta
        self.provincia = provincia
        self.partita_iva = partita_iva
        self.codice_fiscale = codice_fiscale
        self.email = email
        self.codice_sdi = codice_sdi
        self.telefono = telefono
        self.banca = banca
        self.iban = iban
        self.ragione_sociale = ragione_sociale

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
        brand = Brand.query.all()

        # lista di clienti
        customers = Clienti.query.all()


        # lista ordini se admin tutto se agent --> partial
        if session["type"] == "admin":
            orders = Ordini.query.all()
        else:
            orders = Ordini.query.filter_by(author=session["username"]).all()

        ordini = []
        for i in orders:
            ordini.append(i)

        ordini.reverse()


    except:
        print("-- error in fetchin data for routing ---")
    try:
        errore = "nessuno"

        if request.form["value"] == "clienti":
            errore = "in clienti"
            return render_template("clienti.html", clienti=customers)

        elif request.form["value"] == "aggiungi_cliente" :
            return render_template("crea_cliente.html")
        elif request.form["value"] == "rimuovi_cliente":
            return render_template("elimina_cliente.html", clienti=customers)

        elif request.form["value"] == "ordini" :
            errore = "in ordini"
            return render_template("ordini.html", ordini=ordini)

        elif request.form["value"] == "espositore":
            # effettuare distinzione admin agent
            return render_template("manage_admin.html", nomi_brand=brand)

        elif request.form["value"] == "account":
            return render_template("account.html")

        elif request.form["value"] == "upload":
            return render_template("upload.html")
        #modifica ordine
        elif request.form["value"] == "modifica_ordine":
            return render_template("modify-order.html")
        #crea ordine
        elif request.form["value"] == "crea_ordine":

            return render_template("crea_ordine.html", clienti=customers, carrello=carrello, totale=spesa)
        print("non trova nessun route da soddisfare in function routing")


    except:
        global frase
        print("nessuna frase in routing")

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
        biagio = Utenti(username, generate_password_hash(password), 1)
        db.session.add(biagio)
        db.session.commit()
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
            return render_template('home.html', error_pass=errore)


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
            new_utente = Utenti(request.form["email"], generate_password_hash(password_generata))
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

    if request.form["tipo"] == "update":
        try:
            result = Ordini.query.filter_by(codice=request.form["ordine_numero"]).first()
            cliente = Clienti.query.filter_by(ragione_sociale=request.form["ragione_sociale"]).first()
            result.pagamento = request.form["pagamento"]
            result.data = request.form["data"]
            result.cliente = cliente.codice_fiscale
            db.session.commit()

            # non effettua update del carrello ma solo dati dal form
            # ma si potrebbe fare inserendo roba nel carrello e poi aggiornando l'ordine
            # da qui tramite modifica

            print(result)
            return redirect(url_for("home"))
        except:
            print("update failed in adding_orders")
    else:
        # altrimenti è una nuova creazione col tasto crea ordini dando per scontato che il carrello
        # sia pieno!

        try:
            cliente = Clienti.query.filter_by(ragione_sociale=request.form["ragione_sociale"]).first()
            ordine = Ordini(session["username"], request.form["data"], spesa, cliente.codice_fiscale,
                            request.form["pagamento"])
            db.session.add(ordine)
            db.session.commit()
            error = "ordine aggiunto correttamente in adding_orders"

        except:
            error = "erreo aggiunta ordine in adding_orders"

        carrello.clear()
        spesa=0
        print(error)

    global frase, back_to
    frase = "ordine avvenuto con successo"
    back_to = "ordini"
    if session["type"] == "admin":

        return redirect(url_for("routing"))
    else:
        return redirect(url_for("routing"))


@app.route('/modifica_ordine', methods=["POST"])
def modifica_ordine():
    print("modifica ordine in modifica_ordine")
    # retrieve of the order with the form value, value is the unicode of the order
    ordine_retrieve = Ordini.query.filter_by(codice=request.form["value"])

    return render_template("modify-order.html", ordine=ordine_retrieve)


@app.route('/elimina_ordine', methods=['POST'])
def elimina_ordine():

    try:
        retrieved = Ordini.query.filter_by(codice=request.form["value"]).first()
        db.session.delete(retrieved)
        db.session.commit()

        cursore = Ordini.query.filter_by().all()
    except:
        print("errore in deleting in elimina_ordine ")

    return render_template("ordini.html", ordini=cursore)


# aggiunta cliente nel db
@app.route('/adding_customer', methods=['POST'])
def adding_customer():
    customer = Clienti(request.form["nome"], request.form["cognome"], request.form["via"], request.form["cap"]
                       , request.form["città"], request.form["provincia"], request.form["partita_iva"],
                       request.form["codice_fiscale"],
                       request.form["email"], request.form["codice_sdi"], request.form["telefono"],
                       request.form["banca"],
                       request.form["iban"])
    db.session.add(customer)
    db.session.commit()

    return render_template("welcome.html", frase="Cliente aggiunto", back_to="clienti")


# rimozione cliente nel db
@app.route('/removing_customer', methods=['POST'])
def removing_customer():
    retrieved = Clienti.query.filter_by(ragione_sociale=request.form["cliente-da-eliminare"]).first()
    db.session.delete(retrieved)
    db.session.commit()

    return render_template("welcome.html", frase="Cliente rimosso", back_to="clienti")




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_info', methods=['POST'])
def upload_info_file():

    for i in nomi_file:
        gioiello = Gioielli(request.form["brand"], request.form["album"], i, float(request.form[f"prezzo{i}"]),
                            request.form[f"codice_id{i}"])
        db.session.add(gioiello)
        db.session.commit()

    # devo inserire anche il brand
    brand = Brand(request.form["brand"])
    db.session.add(brand)
    db.session.commit()

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
    brand = Gioielli.query.filter_by(brand=request.form["value"])
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
