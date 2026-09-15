// theme + lamp toggle — no framework, no build step.
(function(){
  "use strict";
  var root = document.documentElement;
  var KEY = "ra_theme";

  function apply(theme){
    if(theme === "light" || theme === "dark"){
      root.setAttribute("data-theme", theme);
    } else {
      root.removeAttribute("data-theme"); // follow system
    }
  }

  var saved = null;
  try{ saved = localStorage.getItem(KEY); }catch(e){}
  apply(saved);

  document.addEventListener("DOMContentLoaded", function(){
    var btn = document.querySelector("[data-lamp]");
    if(!btn) return;
    btn.addEventListener("click", function(){
      var current = root.getAttribute("data-theme");
      var isDark = current === "dark" || (!current && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var next = isDark ? "light" : "dark";
      apply(next);
      try{ localStorage.setItem(KEY, next); }catch(e){}
    });
  });
})();
