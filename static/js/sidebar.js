function toggleSidebar() {
  const isWideScreen = window.innerWidth >= 1110;
  resizeableDiv.classList.toggle("w-64", isWideScreen);
  resizeableDiv.classList.toggle("w-0", !isWideScreen);
  /* mainContent.classList.toggle("ml-[14.5rem]", isWideScreen)
  mainContent.classList.toggle("ml-10", !isWideScreen)

  for (const elem of allsidebarTextElem) {
    elem.classList.toggle("scale-0", !isWideScreen);
  }

  for (const elem of allSideBarIcons) {
    elem.classList.toggle("rotate-[360deg]", !isWideScreen);
  } */
}


function toggleSidebarOnHover(show) {
  const isWideScreen = window.innerWidth >= 1110;
  if (isWideScreen){return}
  resizeableDiv.classList.toggle("w-64", show);
  resizeableDiv.classList.toggle("w-0", !show);

  /* for (const elem of allsidebarTextElem) {
    elem.classList.toggle("scale-0", !show);
  }

  for (const elem of allSideBarIcons) {
    elem.classList.toggle("rotate-[360deg]", !show);
  } */
}

function resizeWindow() {
  toggleSidebar();
}

const resizeableDiv = document.getElementById("default-sidebar");
/* const allSideBarIcons = document.getElementsByClassName("sidebarIcon");
const allsidebarTextElem = document.getElementsByClassName("sidebarText"); */
//const mainContent = document.getElementById("mainContent")

document.addEventListener("DOMContentLoaded", () => {
  toggleSidebar(); // Initial state based on window width
  window.addEventListener("resize", resizeWindow);
  resizeableDiv.addEventListener("mouseover", ()=>{toggleSidebarOnHover(true)});
  resizeableDiv.addEventListener("mouseleave", ()=>{toggleSidebarOnHover(false)});
});
