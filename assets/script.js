// Tema claro/oscuro, correo protegido y filtro del archivo. Sin dependencias.
(function(){
  "use strict";
  var root = document.documentElement;
  var KEY = "ra_theme";

  function systemDark(){
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  // Lámpara: alterna y recuerda la preferencia de quien visita.
  var lamp = document.querySelector("[data-lamp]");
  if(lamp){
    var sync = function(){
      var t = root.getAttribute("data-theme");
      var dark = t === "dark" || (!t && systemDark());
      lamp.setAttribute("aria-pressed", dark ? "true" : "false");
    };
    sync();
    lamp.addEventListener("click", function(){
      var t = root.getAttribute("data-theme");
      var dark = t === "dark" || (!t && systemDark());
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try{ localStorage.setItem(KEY, next); }catch(e){}
      sync();
    });
  }

  // Correo: la dirección está invertida en data-e y sólo se arma aquí.
  var links = document.querySelectorAll("a[data-e]");
  for(var i = 0; i < links.length; i++){
    var addr = links[i].getAttribute("data-e").split("").reverse().join("");
    links[i].href = "mailto:" + addr;
    if(links[i].classList.contains("btn")){
      links[i].title = addr;
    }
  }

  // Filtro por tipo en el archivo de obra. Sin JS la lista completa sigue visible.
  var bar = document.querySelector(".filters");
  var archive = document.querySelector("[data-archivo]");
  if(!bar || !archive) return;
  var buttons = bar.querySelectorAll("button[data-filtro]");
  var entries = archive.querySelectorAll(".entry");
  var years = archive.querySelectorAll(".year");

  function apply(tipo){
    var valid = false;
    for(var b = 0; b < buttons.length; b++){
      if(buttons[b].getAttribute("data-filtro") === tipo) valid = true;
    }
    if(!valid) tipo = "todo";
    for(var j = 0; j < buttons.length; j++){
      buttons[j].setAttribute("aria-pressed", buttons[j].getAttribute("data-filtro") === tipo ? "true" : "false");
    }
    for(var k = 0; k < entries.length; k++){
      entries[k].hidden = !(tipo === "todo" || entries[k].getAttribute("data-tipo") === tipo);
    }
    for(var y = 0; y < years.length; y++){
      years[y].hidden = !years[y].querySelector(".entry:not([hidden])");
    }
  }

  bar.hidden = false;
  bar.addEventListener("click", function(ev){
    var btn = ev.target.closest("button[data-filtro]");
    if(!btn) return;
    var tipo = btn.getAttribute("data-filtro");
    apply(tipo);
    try{ history.replaceState(null, "", tipo === "todo" ? location.pathname : "#" + tipo); }catch(e){}
  });
  apply(location.hash.replace("#", "") || "todo");
})();
