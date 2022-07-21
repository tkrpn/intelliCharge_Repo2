
(function () {
    let dropdown = document.querySelector(".dropdown");

    function selectDropdownMenu(dropdown) {
      let dropdownMenu = document.querySelector(".dropdown--menu");
      let selectInput = document.querySelector(".select-input");
      let selectText = document.querySelector(".select-text");
      let dropdownMenuList = document.querySelectorAll(".dropdown--menu li");
      dropdown.addEventListener("click", (e) => {
        e.currentTarget.classList.toggle("rotate");
        dropdownMenu.classList.toggle("active");
      });
      Array.from(dropdownMenuList).forEach((element) => {
        element.addEventListener("click", (e) => {
          let text = e.currentTarget.getAttribute("data-text");
          let value = e.currentTarget.getAttribute("data-value");
          selectInput.value = value;
          selectText.innerHTML = text;
          dropdown.classList.remove("rotate");
          dropdownMenu.classList.remove("active");
        });
      });
    }    
    if (dropdown != null) selectDropdownMenu(dropdown);

    // start coding for slider


    const range = document.querySelector(".range-input"),
      tooltip = document.querySelector(".move-value"),
      setValue = () => {
        const newValue = Number(
            ((range.value - range.min) * 100) / (range.max - range.min)
          ),
          newPosition = 16 - newValue * 0.32;
        tooltip.innerHTML = range.value +"%";
        tooltip.style.left = `calc(${newValue}% + (${newPosition}px))`;
      };
    document.addEventListener("DOMContentLoaded", setValue);
    range.addEventListener("input", setValue);

})()