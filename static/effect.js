// JavaScript Document
/*
var array = [["clienti", "sezione-clienti"], ["ordini", "sezione-ordini"], ["account", "sezione-account"], ["espositore", "sezione-espositore"], ["agg-cliente", "sezione-add-clienti"], ["crea-ordine", "sezione-crea-ordine"]];


//event listener on ...
document.getElementById("clienti").addEventListener("click", function () {
    highlight("clienti");
});
document.getElementById("agg-cliente").addEventListener("click", function () {
    highlight("agg-cliente");
});
document.getElementById("indietro-ordine").addEventListener("click", function () {
    highlight("ordini");
});
document.getElementById("crea-ordine").addEventListener("click", function () {
    highlight("crea-ordine");
});
document.getElementById("indietro-cliente").addEventListener("click", function () {
    highlight("clienti");
});
document.getElementById("ordini").addEventListener("click", function () {
    highlight("ordini");
});
document.getElementById("account").addEventListener("click", function () {
    highlight("account");
});
document.getElementById("espositore").addEventListener("click", function () {
    highlight("espositore");
});
document.getElementById("hamburgher").addEventListener("click", function () {
    menu_open();
});
document.getElementById("img-close").addEventListener("click", function () {
    menu_close();
});
document.getElementById("exit").addEventListener("click", function () {
    menu_close();
});

//funzione per effetto evidenziatore menu
function highlight(id) {
    var c, i;
    for (c = 0; c < array.length; c++) {
        if (array[c][0] == id) {
            break;
        }
    }
    console.log(array[c][1]);
    document.getElementById(id).style.backgroundColor = "yellow";
    document.getElementById(array[c][1]).style.left = "0em";
    for (i = 0; i < array.length; i++) {
        if (array[i][0] != id) {
            document.getElementById(array[i][0]).style.backgroundColor = "transparent";
            document.getElementById(array[i][1]).style.left = "-100em";
        }

    }
}
*/


/*funzione apertura menu*/
function menu_open() {
    document.getElementById("exit").style.display = "block";
    document.getElementById("menu-scomp").style.right = "0";
    setTimeout(function () {
        document.getElementById("hamburgher").style.display = 'none';
    }, 1000);


}

/*funzione chiusura menu*/
function menu_close() {
    document.getElementById("exit").style.display = "none";
    document.getElementById("hamburgher").style.display = 'block';
    document.getElementById("menu-scomp").style.right = "-55vw";
}

document.getElementById("nav").addEventListener("mouseover", function () {
    sfoca();

});
document.getElementById("nav").addEventListener("mouseout", function () {
    rifoca();

});

function sfoca() {
    console.log("sfoco");
    document.getElementById("container-fluid").style.filter = "blur(2.5px)";

}

function rifoca() {
    console.log("rifoco");
    document.getElementById("container-fluid").style.filter = "blur(0px)";

}


/* AJAX REQUEST for albums*/
function http(url, target, value) {
    console.log("GET me " + url + " to " + target + " " + value);
    if (url == "/svuota_carrello") {
        document.getElementById("cart").innerHTML = "€"
    }
    const Http = new XMLHttpRequest();
    var qui = document.getElementById(target);
    Http.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            qui.innerHTML = this.responseText;
        } else {
            qui.innerHTML = this.status;
        }
    };
    console.log(value)
    Http.open("POST", url, true);
    Http.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    Http.send("value=" + value);
}

/* AJAX REQUEST for albums*/
function http_cart(url, codice) {


    if (url == "/add_to_cart") {
        document.getElementById(codice + "radio").checked = true;
    } else {
        document.getElementById(codice + "radio").checked = false;
    }
    id_codice = '#' + codice + "quantita";
    prezzo_codice = codice + "prezzo";
    var quantita = $(id_codice).val();
    var prezzo = document.getElementById(prezzo_codice).innerHTML;
    prezzo = prezzo.replace(",", ".");

    var data = [codice, quantita, prezzo];
    const Http = new XMLHttpRequest();
    var qui = document.getElementById("cart");


    Http.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            qui.innerHTML = this.responseText;

        } else {
            qui.innerHTML = 0;
        }

    }


    Http.open("POST", url, true);
    Http.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    Http.send("data=" + data);

}

