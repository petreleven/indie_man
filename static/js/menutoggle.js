var menubtn = document.getElementById("menu");
var menubar = document.getElementById("menubar");
menubtn.addEventListener("click", (e) => {
  menubar.classList.toggle("hidden");
});
