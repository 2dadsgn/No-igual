// JavaScript Document
var array = [["clienti", "sezione-clienti"], ["ordini", "sezione-ordini"], ["account", "sezione-account"], ["espositore", "sezione-espositore"], ["agg-cliente", "sezione-add-clienti"], ["crea-ordine", "sezione-crea-ordine"]];

/*event listeners*/
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

/*funzione per effetto evidenziatore menu*/
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