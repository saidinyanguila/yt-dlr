const like_btn = document.getElementById("btn_00");
const id = like_btn.getAttribute("data-id");

const handle_click = async () => {
    fetch("/library/like_album", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            id: id
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.liked) {
            document.getElementById("icn_00").classList.add("fill-black")
        }
        else {
            document.getElementById("icn_00").classList.remove("fill-black")
        }
    })
}

like_btn.addEventListener("click", handle_click);