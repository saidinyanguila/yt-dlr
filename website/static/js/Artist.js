const followBtn = document.getElementById("btn_00");
const id = followBtn.getAttribute("data-id");

const handle_click = async () => {
    fetch("/library/follow_artist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            id: id
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.followed) {
            followBtn.classList.replace("bg-red-400", "bg-gray-400")
            followBtn.innerHTML = "Following";
        }
        else {
            followBtn.classList.replace("bg-gray-400", "bg-red-400")
            followBtn.innerHTML = "Follow";
        }
    })
}

followBtn.addEventListener("click", handle_click);