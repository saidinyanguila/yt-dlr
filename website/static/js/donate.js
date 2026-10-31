const radios = document.querySelectorAll('input[name="amount"]');
const own_amt = document.getElementById("own_amount");
const own_amt_btn = document.getElementById("own_amount_btn");
const own_amt_section = document.getElementById("own_amount_section");

radios.forEach(radio => {
    radio.addEventListener('change', (event) => {
        own_amt_btn.removeAttribute("disabled");

        if (event.target.value == 0) {
            own_amt_section.classList.add("open");
            own_amt.setAttribute("required", true);
        }
        else { 
            own_amt_section.classList.remove("open");
            own_amt.removeAttribute("required");
            own_amt.value = "";
        }
    });
});