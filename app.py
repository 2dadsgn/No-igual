import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
from random_password import random_password
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# modificare prima di caricare /home/pi/Desktop/untitled/static
UPLOAD_FOLDER = '/Users/labieno/PycharmProjects/untitled/static'
#UPLOAD_FOLDER = '/home/pi/Desktop/untitled/static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
mail = Mail(app)

# config for the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# app.config["MONGO_URI"] = "mongodb://localhost:27017/db-noigual"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///noigual.sqlite3'
# mongo = PyMongo(app)
db = SQLAlchemy(app)
app.secret_key = b'_52ksaLFwerWWrcdesal'

app.config['MAIL_SERVER'] = 'out.virgilio.it'
app.config['MAIL_PORT'] = 465
sender_email = 'infonoigualgioielli@virgilio.it'
app.config['MAIL_USERNAME'] = 'infonoigualgioielli@virgilio.it'
app.config['MAIL_PASSWORD'] = 'hvwbA3uH7K24DVd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# DB models###############

# utenti-------------
class Utenti(db.Model):
    email = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)
    poteri = db.Column(db.Integer, default=0)
    approvato = db.Column(db.Integer, default=0)
    ordini = db.relationship('Ordini', backref='utente', lazy=True)

    def __init__(self, email, password, poteri, approvato):
        self.email = email
        self.password = password
        self.poteri = poteri
        self.approvato = approvato


# gioielli------------
class Gioielli(db.Model):
    brand = db.Column(db.String(30), db.ForeignKey('brand.nome'))
    categoria = db.Column(db.Integer, db.ForeignKey('categorie.unicode'))
    immagine = db.Column(db.String(50), nullable=False, default='140X140.gif')
    prezzo = db.Column(db.Float, nullable=False)
    codice = db.Column(db.String(30), primary_key=True)

    def __init__(self, immagine, prezzo, codice, brand, categoria):

        self.immagine = immagine
        self.prezzo = prezzo
        self.codice = codice
        self.brand = brand
        self.categoria = categoria
# -------------------------

# ---------BRAND----------
class Brand(db.Model):
    nome = db.Column(db.String(20), primary_key=True)
    img = db.Column(db.String(30), nullable=True, default='140X140.gif')
    categorie = db.relationship('Categorie', backref='category', lazy=True)
    oggetto = db.relationship('Gioielli', backref='marca', lazy=True)
    ordinati = db.relationship('Gioielli_Ordinati', backref='marca', lazy=True)

    def __init__(self, nome, img):
        self.nome = nome
        self.img = img


# --------------------


# ---------categorie----------
class Categorie(db.Model):
    unicode = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)
    brand = db.Column(db.String(30), db.ForeignKey('brand.nome'), nullable=False)
    gioielli = db.relationship('Gioielli', backref='categ', lazy=True)
    ordinati = db.relationship('Gioielli_Ordinati', backref='category', lazy=True)
    img = db.Column(db.String(30), nullable=True, default='140X140.gif')

    def __init__(self, nome, brand, img):
        self.nome = nome
        self.brand = brand
        self.img = img



# ordini------------
class Ordini(db.Model):
    author = db.Column(db.String(30), db.ForeignKey('utenti.email'), nullable=False)
    codice = db.Column(db.Integer, primary_key=True)
    data_esecuzione = db.Column(db.String(20), nullable=False)
    data_consegna = db.Column(db.String(20), nullable=False)
    totale = db.Column(db.Float, nullable=False)
    cliente = db.Column(db.String(30), db.ForeignKey('clienti.codice_fiscale'), nullable=False)
    pagamento = db.Column(db.String(20), nullable=False)
    carrello = db.relationship('Gioielli_Ordinati', backref='ordine', lazy=True)

    def __init__(self, author, data_esecuzione, data_consegna, totale, cliente, pagamento):
        self.author = author
        self.data_esecuzione = data_esecuzione
        self.data_consegna = data_consegna
        self.totale = totale
        self.cliente = cliente
        self.pagamento = pagamento


# -------------------------


# gioielli ordinati------------
class Gioielli_Ordinati(db.Model):
    unicode = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(30), db.ForeignKey('brand.nome'), nullable=False)
    categoria = db.Column(db.Integer, db.ForeignKey('categorie.unicode'), nullable=False)
    immagine = db.Column(db.String(50), nullable=False, default='140X140.gif')
    prezzo = db.Column(db.Float, nullable=False)
    quantita = db.Column(db.Integer, default=1)
    codice_barre = db.Column(db.String(30), db.ForeignKey('gioielli.codice'), nullable=False)
    codice_ordine = db.Column(db.Integer, db.ForeignKey('ordini.codice'), nullable=False)

    def __init__(self, brand, categoria, immagine, prezzo, codice_barre, codice_ordine, quantita):
        self.brand = brand
        self.categoria = categoria
        self.immagine = immagine
        self.prezzo = prezzo
        self.codice_barre = codice_barre
        self.codice_ordine = codice_ordine
        self.quantita = quantita
# -------------------------


# clienti------------
class Clienti(db.Model):
    nome = db.Column(db.String(10), nullable=False)
    cognome = db.Column(db.String(15), nullable=False)
    via = db.Column(db.String(30), nullable=False)
    cap = db.Column(db.Integer, nullable=False)
    citta = db.Column(db.String(20), nullable=False)
    provincia = db.Column(db.String(4), nullable=False)
    partita_iva = db.Column(db.String(30), nullable=False, unique=True)
    codice_fiscale = db.Column(db.String(40), primary_key=True)
    email = db.Column(db.String(30), nullable=True)
    email_pec = db.Column(db.String(30), nullable=True)
    codice_sdi = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    banca = db.Column(db.String(30), nullable=False)
    iban = db.Column(db.String(30), nullable=False)
    ragione_sociale = db.Column(db.String(40), nullable=False, unique=True)
    ordini = db.relationship('Ordini', backref='ordinato_da', lazy=True)
    author = db.Column(db.String(30), db.ForeignKey('utenti.email'), nullable=False)

    def __init__(self, nome, cognome, via, cap, citta, provincia, partita_iva, codice_fiscale, email, pec, codice_sdi,
                 telefono, banca, iban, ragione_sociale, author):
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
        self.email_pec = pec

# -------------------------


#########################

app.host = '0.0.0.0'

# global clients code
codice_clienti = 0

# nomifile global
nomi_file = []

# global spesa
spesa = 0.0

# global brand in visualizzazione
brand_attuale = "none"
categoria_attuale = "none"

# carrello
carrello = []

# quantity
quantity = {
    " ": None
}

# global per routing
frase = "null"
back_to = "null"

# array per briciole di pane in espositore
prev = []



@app.route('/')
def index():
    return render_template("home.html")


@app.route('/routing', methods=["POST", "GET"])
def routing():
    global indice_ordini, carrello, spesa, frase, back_to  # aggiunta qui ultimamente spesa
    try:
        # lista di brand
        brand = Brand.query.all()
    except:
        print("-- error in fetchin brand for routing ---")
    try:

        # lista ordini se admin tutto se agent --> partial
        if session["type"] == "admin":
            # lista di clienti
            customers = Clienti.query.all()
        else:
            # lista di clienti
            # customers = Clienti.query.filter_by(author=session["username"])
            print("nessun clienti restituito per rappresentante")

    except:
        print("-- error in fetchin clienti for routing ---")

    try:
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
        print("-- error in fetchin ordini for routing ---")

    try:
        # lista utenti
        if session["type"] == "admin":
            utenti = Utenti.query.all()

    except:
        print("-- error in fetchin utenti for routing ---")




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
            utente = Utenti.query.filter_by(email=session["username"]).first()
            if utente.poteri == 1:
                return render_template("account.html", utenti=utenti)
            else:
                frase = "Non si dispone delle autorizzazioni necessarie"
                back_to = "espositore"

        elif request.form["value"] == "upload":
            return render_template("upload.html")
        #modifica ordine
        elif request.form["value"] == "modifica_ordine":
            return render_template("modify-order.html")
        #crea ordine
        elif request.form["value"] == "crea_ordine":
            # c'è un errore in fetchin con codice a barre perchè gioielli ordinati unicode non barre
            gioielli_carrello = []
            gioielli_carrello.clear()
            for i in carrello:
                temp = Gioielli.query.filter_by(codice=i).first()
                gioielli_carrello.append(temp)

            return render_template("crea_ordine.html", clienti=customers, carrello=gioielli_carrello,
                                   quantita=quantity, totale=spesa)

        print("non trova nessun route da soddisfare in function routing")


    except:

        print("nessun route richiesto")



    if frase == "Benvenuto" and session["username"]:
        frase = "Benvenuto " + session["username"]
    elif session["username"] == "" or session["username"] == None:
        render_template("home.html")
    return render_template("welcome.html", frase=frase, back_to=back_to)




@app.route('/logging', methods=["POST"])
def logging():
    global frase, back_to
    username = request.form["username"]
    password = request.form["password"]

    # ricerca utente in DB
    cursore = Utenti.query.filter_by(email=username).first()

    if cursore == None:
        biagio = Utenti(username, generate_password_hash(password), 0, 0)
        db.session.add(biagio)
        db.session.commit()
        errore = "utente registrato, in attesa di approvazione"
        return render_template('home.html', error_name=errore)

    else:
        if cursore.approvato == 0:
            errore = "utente non ancora approvato"
            return render_template('home.html', error_pass=errore)

        elif check_password_hash(cursore.password, password):
            if cursore.poteri == 1:
                tipo_utente = "admin"
                session["type"] = "admin"
                session["username"] = request.form["username"]
                frase = "Benvenuto"
                back_to = "null"
                return redirect(url_for("routing"))  # call the method home to load fresh data on access

            else:
                tipo_utente = "rappresentante"
                session["type"] = "agent"
                session["username"] = request.form["username"]
                frase = "Benvenuto"
                back_to = "null"
                return redirect(url_for("routing"))  # call the method home to load fresh data on access
        else:
            errore = "password errata"
            return render_template('home.html', error_pass=errore)


@app.route('/approva_utente', methods=["POST"])
def approvva_utente():
    global frase, back_to
    try:
        utente = Utenti.query.filter_by(email=request.form["value"]).first()
        if utente.approvato == 0:
            valore = "abilitato"
            utente.approvato = 1
        else:
            valore = "disabilitato"
            utente.approvato = 0
        db.session.commit()

    except:
        print("errore in approvazione/disapprovazione utente")
        frase = "Errore in /approva_utente "
        back_to = "account"
        return redirect(url_for("routing"))

    frase = f"utente {valore} con successo"
    back_to = "account"
    return redirect(url_for("routing"))


@app.route('/rimuovi_utente', methods=["POST"])
def rimuovi_utente():
    global frase, back_to
    try:

        utente = Utenti.query.filter_by(email=request.form["value"]).first()

        # se l'utente da cancellare è diverso da quello della sessione corrente
        # effettua eliminazione altrimenti ritorna errrore
        if (utente.email == session["username"]):
            # do nothing
            frase = f"impossibile eliminare utente sessione attuale"
        else:
            db.session.delete(utente)
            db.session.commit()
            frase = f"utente rimosso con successo"

    except:
        print("errore eliminazione utente")
        frase = "Errore in eliminazione_utente "
        back_to = "account"
        return redirect(url_for("routing"))


    back_to = "account"
    return redirect(url_for("routing"))


def sending_email(destinatario):
    try:
        token = random_password(length=6,
                                characters=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'M', 'a', 'b', 'c', 'd',
                                            'e',
                                            'f'
                                    , 'g', 'h', 'i', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't'
                                    , 'u', 'v', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

        msg = Message('Accesso credenziali', sender=sender_email, recipients=[f"{destinatario}"])
        msg.body = f"""ciao  {destinatario} , conserva queste informazioni accuratamente,
            ti abbiamo appena inviato le credenziali di accesso per l'espositore online di No 
            Igual gioielli, questa è la tua password --> {token} <--  """
        mail.send(msg)
    except:
        print("errore in invio email")
        token = "errore"
    return token


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
            new_utente = Utenti(request.form["email"], generate_password_hash(password_generata), 0, 1)
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
        return ' <h4>Inserisci nuova email</h4> <input class="dritto" type="email" name="email" value="">' + '<p>La password sarà generata automaticamente<br> e inviata via email</p>' + '<input class="dritto" type="submit" value="Procedi">'
    else:
        return '<h4 class="dritto">Inserisci vecchia email</h4><input class="dritto " type="email" name="vecchia-email" value=""><h4>Inserisci nuova email</h4><input class="dritto" type="email" name="email" value=""><p>La password sarà generata automaticamente<br> e inviata via email</p><input class="dritto" type="submit" value="Procedi">'






@app.route('/adding_orders', methods=["POST"])
def adding_orders():
    global carrello, spesa, frase, back_to
    data_esecuzione = datetime.date.today()

    try:
        cliente = Clienti.query.filter_by(ragione_sociale=request.form["ragione_sociale"]).first()
        ordine = Ordini(session["username"], data_esecuzione, request.form["data"], spesa, cliente.ragione_sociale,
                        request.form["pagamento"])

        db.session.add(ordine)

        db.session.commit()
        t =0

        for i in carrello:
            gioiello = Gioielli.query.filter_by(codice=i).first()
            gioiello_ordinato = Gioielli_Ordinati(gioiello.brand, gioiello.categoria, gioiello.immagine,
                                                  gioiello.prezzo, gioiello.codice, ordine.codice, quantity[i])

            db.session.add(gioiello_ordinato)
            db.session.commit()
            t = t +1
        carrello.clear()
        quantity.clear()
        spesa = 0
        error = 0
        ordine = Ordini.query.all()
        for i in ordine:
            i
        stampa(i.codice)
    except:
        error = 1


    if error == 1:
        frase = "errore imprevisto nell'aggiunta ordine"
    else:
        frase = "ordine avvenuto con successo"

    back_to = "ordini"

    return redirect(url_for("routing"))


@app.route('/modifica_ordine', methods=["POST"])
def modifica_ordine():
    print("modifica ordine in modifica_ordine")
    # retrieve of the order with the form value, value is the unicode of the order
    ordine = Ordini.query.filter_by(codice=request.form["value"]).first()
    clienti = Clienti.query.all()

    return render_template("modify-order.html", ordine=ordine, clienti=clienti)


@app.route('/modifica!', methods=["POST"])
def modifica_ordine_effetttuata():
    # retrieve of the order with the form value, value is the unicode of the order
    ordine = Ordini.query.filter_by(codice=request.form["codice"]).first()
    ordine.data = request.form["data"]
    ordine.pagamento = request.form["pagamento"]
    ordine.cliente = request.form["cliente"]
    db.session.commit()

    return render_template("modify-order.html", ordine=ordine)


@app.route('/elimina_ordine', methods=['POST'])
def elimina_ordine():

    try:

        Ordini.query.filter_by(codice=request.form["value"]).delete()

        while Gioielli_Ordinati.query.filter_by(codice_ordine=request.form["value"]).all():
            Gioielli_Ordinati.query.filter_by(codice_ordine=request.form["value"]).delete()
        db.session.commit()



    except:
        print("errore in deleting in elimina_ordine ")

    try:
        if session["type"] == "admin":
            cursore = Ordini.query.filter_by(author=session["username"]).all()
        else:
            cursore = Ordini.query.filter_by(author=session["username"]).all()
    except:
        print ("errore in fetchin ordini dopo eliminazione ordine")

    tmp = []
    tmp.clear()
    for i in cursore:
        tmp.append(i)
    tmp.reverse()

    return render_template("ordini.html", ordini=tmp)




# aggiunta cliente nel db
@app.route('/adding_customer', methods=['POST'])
def adding_customer():
    customer = Clienti(request.form["nome"], request.form["cognome"], request.form["via"], request.form["cap"]
                       , request.form["città"], request.form["provincia"], request.form["partita_iva"],
                       request.form["codice_fiscale"], request.form["email"], request.form["email_pec"],
                       request.form["codice_sdi"],
                       request.form["telefono"], request.form["banca"], request.form["iban"],
                       request.form["ragione_sociale"], session["username"])
    db.session.add(customer)
    db.session.commit()

    return render_template("welcome.html", frase="Cliente aggiunto", back_to="clienti")


# rimozione cliente nel db
@app.route('/removing_customer', methods=['POST'])
def removing_customer():
    Clienti.query.filter_by(ragione_sociale=request.form["cliente-da-eliminare"]).delete()
    db.session.commit()

    return render_template("welcome.html", frase="Cliente rimosso", back_to="clienti")




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_info', methods=['POST'])
def upload_info_file():
    global frase, back_to

    # prova a creare il brand se fallisce esiste già
    if Brand.query.filter_by(nome=request.form["brand"]).first():
        # do nothing
        print("brand già esistente")
    else:
        brand = Brand(request.form["brand"], nomi_file[0])
        db.session.add(brand)
        db.session.commit()

    try:
        immagine = nomi_file[1]
    except:
        immagine = nomi_file[0]

    if Categorie.query.filter_by(nome=request.form["album"], brand=request.form["brand"]).first():
        # do nothing
        print("categoria già esistente")
    else:
        categoria = Categorie(request.form["album"], request.form["brand"], immagine)
        db.session.add(categoria)
        db.session.commit()



    for i in nomi_file:

        # escamotage per trasformare stringa con , in float  con .

        try:

            prezzo = float(request.form[f"prezzo{i}"])

        except:

            tmp = []

            tmp.append(request.form[f"prezzo{i}"].rsplit(',', 1)[0])

            tmp.append(request.form[f"prezzo{i}"].rsplit(',', 1)[1])

            prezzo = tmp[0] + "." + tmp[1]

            prezzo = float(prezzo)


        cat = Categorie.query.filter_by(nome=request.form["album"], brand=request.form["brand"]).first()

        gioiello = Gioielli(i, str(prezzo), request.form[f"codice_id{i}"], request.form["brand"], cat.unicode)

        db.session.add(gioiello)
        db.session.commit()

    frase = "upload avvenuto con successo"
    back_to = "espositore"

    return redirect(url_for("routing"))


@app.route('/uploading', methods=['POST'])
def upload_file():
    global frase, back_to
    nomi_file.clear()  #pulisco array per evitare sovrapposizioni in upload successivi
    if request.method == 'POST' :

        file = request.files.getlist("file")

        t=0

        for i in file:
            nomefile = i.filename.replace("(", "")
            nomefile = nomefile.replace(")", "")
            nomi_file.append(nomefile.replace(" ","_"))

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

        print("lista nomi file")

        # qui loop for per save multiple files
        for t in file:
            if t and allowed_file(t.filename):
                filename = secure_filename(t.filename.replace(" ", "_"))
                print(filename)
                t.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print("fine lista nomi file")

        return render_template("upload.html", nomi_file=nomi_file,
                               album=request.form["album"], brand=request.form["brand"])
    return render_template("welcome.html", frase="Errore in upload file")


@app.route('/ricerca_oggetto', methods=['POST'])
def ricerca_oggetto():
    global trovato, back_to, frase
    try:
        gioiello = Gioielli.query.filter_by(codice=request.form["codice"]).first()
        print(gioiello.codice)

    except:
        frase = "Ricerca fallita, oggetto non trovato"
        back_to = "account"
        return redirect(url_for('routing'))

    return render_template("modifica_oggetto.html", gioiello=gioiello)


@app.route('/elimina_oggetto', methods=['POST'])
def elimina_oggetto():
    global frase, back_to
    try:
        # controllo if con due cancellazioni se anche album, categoria o solo oggeto
        if request.form["value"] == "multiple":
            print("eliminazione multipla")

            for i in carrello:
                Gioielli.query.filter_by(codice=i).delete()
        else:
            gioiello = Gioielli.query.filter_by(codice=request.form["value"]).delete()

        frase = "eliminazione avvenuta con successo"
        back_to = "espositore"
        db.session.commit()

    except:
        frase = "eliminazione non avvenuta"
        back_to = "espositore"

    return redirect(url_for("routing"))


@app.route('/effettua_modifica_oggetto', methods=['POST'])
def effettua_modifica_oggetto():
    global frase, back_to

    try:
        gioiello = Gioielli.query.filter_by(codice=request.form["vecchio_codice"]).first()
        gioiello.prezzo = request.form["prezzo"]
        gioiello.codice = request.form["codice"]
        db.session.commit()
        frase = "modifica avvenuta con successo"
        back_to = "espositore"
    except:
        frase = "errore"
        back_to = "espositore"


    return redirect(url_for("routing"))




# route per pagina categorie dello specifico brand
@app.route("/espositore", methods=["POST", "GET"])
def mostra_espositore():
    global brand_attuale, prev
    brand_attuale = request.form["value"]
    brand = Brand.query.filter_by(nome=request.form["value"]).first()
    prev.clear()
    prev.append("espositore")

    return render_template("album.html", brand=brand, prev=prev)


#route per pagina gioielli della specifica categoria
@app.route("/categoria", methods=["POST", "GET"])
def mostra_categoria():
    global brand_attuale, categoria_attuale, prev

    categoria = Categorie.query.filter_by(unicode=request.form["value"]).first()
    categoria_attuale = request.form["value"]
    gioielli = categoria.gioielli
    print(brand_attuale, categoria_attuale)
    for i in gioielli:
        print(i)
    prev.clear()
    prev.append("espositore")
    prev.append(brand_attuale)

    return render_template("gioielli.html", album=categoria, gioielli=gioielli, prev=prev)


@app.route("/view_img", methods=["POST", "GET"])
def view_img():
    global brand_attuale, categoria_attuale
    return render_template("view_img.html", url_foto=request.form["value"], categoria=categoria_attuale)

@app.route("/add_to_cart", methods=["POST", "GET"])
def add_to_cart():
    global carrello
    global spesa
    global quantity

    # dati diviene un array
    dati = request.form["data"].split(",")
    carrello.append(dati[0])
    quantity[dati[0]] = dati[1]

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
                prezzo_finale = float(quantity[carrello[i]]) * prezzo
                del quantity[carrello[i]]
                break
    if carrello[i] == codice:
        carrello.remove(codice)
        spesa = round(float(spesa - prezzo_finale),2)

    return f"{spesa}"


@app.route('/svuota_carrello', methods=['POST'])
def svuota_carrello():
    global carrello, spesa, quantity, frase, back_to
    carrello.clear()
    spesa = 0
    quantity.clear()
    frase = "Carrello svuotato"
    back_to = "espositore"
    print("proco dio")

    return redirect(url_for("routing"))


def stampa(ordine_numero):
    try:
        ordine = Ordini.query.filter_by(codice=ordine_numero).first()
        gioielli_ordinati = Gioielli_Ordinati.query.filter_by(codice_ordine=ordine_numero).all()
        cliente = Clienti.query.filter_by(codice_fiscale=ordine.cliente).first()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("times", size=25)
        pdf.cell(40, 10, txt=f"No igual gioielli", ln=0, align="L")
        pdf.set_font("times", size=12)
        pdf.cell(100, 10, txt=f"ordine richiesto da {cliente.ragione_sociale}", ln=1, align="R")
        pdf.cell(140, 10, txt=f"ORDINE numero #{ordine_numero}", ln=1, align="R")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")
        pdf.cell(200, 3, txt=f"Articoli ordinati: ", ln=1, align="C")
        pdf.cell(200, 2, txt="________________________________________________________________________________", ln=1,
                 align="C")
        pdf.cell(65, 5, txt=f" ", ln=0, align="C")
        pdf.cell(20, 5, txt=f"codice", ln=0, align="C")
        pdf.cell(20, 5, txt=f"quantita", ln=0, align="C")
        pdf.cell(20, 5, txt=f"prezzo", ln=1, align="C")
        pdf.cell(200, 5, txt="_________________________________________________________________", ln=1, align="C")
        for i in gioielli_ordinati:
            pdf.cell(65, 5, txt=f" ", ln=0, align="C")
            pdf.cell(20, 5, txt=f"{i.codice_barre}", ln=0, align="C")
            pdf.cell(20, 5, txt=f"{i.quantita}", ln=0, align="C")
            pdf.cell(20, 5, txt=f"{i.prezzo}", ln=1, align="C")
            pdf.cell(200, 5, txt="_________________________________________________________________", ln=1, align="C")
        pdf.cell(10, 10, txt="", ln=0, align="L")
        pdf.cell(100, 10, txt=f"Data creazione ordine {ordine.data_esecuzione}", ln=0, align="L")
        pdf.cell(80, 10, txt=f"Data consegna prevista {ordine.data_consegna}", ln=1, align="R")
        pdf.cell(200, 10, txt=" ", ln=1, align="C")
        pdf.cell(180, 10, txt=f"TOTALE - {ordine.totale} Euro", ln=1, align="R")
        pdf.cell(200, 2, txt="___________________________________________________________________________________",
                 ln=1, align="C")
        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        pdf.add_page()
        pdf.cell(200, 2, txt="Dati del cliente", ln=1, align="C")

        pdf.cell(200, 20, txt=" ", ln=1, align="C")
        # prima riga
        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(40, 2, txt="Nome", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.nome}", ln=0, align="L")

        pdf.cell(40, 2, txt="Cognome", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.cognome}", ln=1, align="LL")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        # seconda riga

        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(40, 2, txt="Codice Fiscale", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.codice_fiscale}", ln=0, align="LL")

        pdf.cell(40, 2, txt="Ragione sociale", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.ragione_sociale}", ln=1, align="LL")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        # terza riga

        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(40, 2, txt="Via", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.via}", ln=0, align="L")

        pdf.cell(40, 2, txt="CAP", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.cap}", ln=1, align="L")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        # quarta riga

        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(40, 2, txt="Città", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.citta}", ln=0, align="L")

        pdf.cell(40, 2, txt="Provincia", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.provincia}", ln=1, align="L")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        # quinta riga

        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(40, 2, txt="Partita IVA", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.partita_iva}", ln=0, align="L")

        pdf.cell(40, 2, txt="Codice SDI", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.codice_sdi}", ln=1, align="L")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        # quinta riga

        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(20, 2, txt="Email", ln=0, align="L")
        pdf.cell(60, 2, txt=f"{cliente.email}", ln=0, align="L")

        pdf.cell(20, 2, txt="Pec", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.email_pec}", ln=1, align="L")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        # SESTA riga

        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(40, 2, txt="Telefono", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.telefono}", ln=0, align="L")

        pdf.cell(40, 2, txt="Banca", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.banca}", ln=1, align="L")

        pdf.cell(200, 10, txt=" ", ln=1, align="C")

        # settima riga

        pdf.cell(20, 20, txt=" ", ln=0, align="C")

        pdf.cell(40, 2, txt="IBAN", ln=0, align="L")
        pdf.cell(40, 2, txt=f"{cliente.iban}", ln=1, align="L")



        pdf.output(f"static/{ordine_numero}.pdf")
    except:
        print ("pdf creation failed")


@app.route('/invia_email_cliente', methods=['POST'])
def invia_email_cliente():
    global frase, back_to
    ordine = Ordini.query.filter_by(codice=request.form["value"]).first()
    cliente = Clienti.query.filter_by(codice_fiscale=ordine.cliente).first()

    try:
        msg = Message('Ordine', sender='provaprovaprova52@virgilio.it', recipients=[f"{cliente.email}"])
        msg.body = f"""Salve le alleghiamo di seguito la ricevuta d'ordine da lei effettuata.
        Cordiali saluti"""
        with app.open_resource(f'static/{ordine.codice}.pdf') as fp:
            msg.attach(f'{ordine.codice}.pdf', "application/pdf", fp.read())
        mail.send(msg)
        frase = "email inviata con successo"
        back_to = "ordini"
    except:
        print("email non inviata al cliente")
        frase = "errore nell'invio dell'email"
        back_to = "ordini"

    return redirect(url_for('routing'))





if __name__ == '__main__':
    app.run()
