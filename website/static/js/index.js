const results = document.querySelectorAll(".search_result");
const errorMessages = ["That's weird..", "Uhm...", "There should be something here..", "This doesn't always happen", "We'll fix this", "Please try again"];
let downloading = false;

results.forEach((res) => {
    const yt_id = res.getAttribute("data-yt-id");
    let interacted = false;
    let isOpen = false;

    const open = () => {
        if (isOpen) return;
        isOpen = true;

        res.querySelector(".search_result_btn").classList.add("open");
        res.querySelector(".search_result_options").classList.remove("hidden");

        if (!interacted) {
            interacted = true;
            search_tracks(res.getAttribute("data-title-clean"));
        }
    }

    const close = (e) => {
        if (!isOpen) return;
        isOpen = false;

        e.stopPropagation();

        res.querySelector(".search_result_btn").classList.remove("open");
        res.querySelector(".search_result_options").classList.add("hidden");
    }

    const search_tracks = (query) => {
        if (query.length < 1) return;
        
        fetch(`/tags/${query}`)
        .then(res => res.json())
        .then(data => {
            render_tracks(query, data)
        })
        .catch(e => {
            console.log(e);
            let randomMsg = Math.round(Math.random() * 5);

            res.querySelector(".tracks_results").innerHTML = `
                <div class="flex flex-col items-center justify-center px-2 py-6">
                    <div class="flex items-center gap-2">    
                        <p class="text-[22px]">${errorMessages[randomMsg]}</p>
                        <i data-lucide="alertTriangle"></i>
                    </div>

                    <p class="text-md">An error occured while searching for this song's info</p>
                </div>
            `;

            lucide.createIcons();
        })
    }

    const render_tracks = (searchQuery, tracks) => {
        res.querySelector(".tracks_results").innerHTML = "";

        if (tracks.length == 0) {
            res.querySelector(".tracks_results").innerHTML = `<div class="py-4 text-center"><h2 class="text-lg">No Result for "${searchQuery}"</h2></div>`
            return;
        }

        for (let i = 0; i < 4; i++) {
            if (!tracks[i]) return;

            let item = document.createElement("div");
            item.className = "relative mb-1 flex items-center justify-between py-1 px-3";
            
            item.innerHTML = `
                <div class="flex items-center">
                    <div class="relative w-[60px] h-[60px] mr-3 aspect-square" >
                        <img class="w-full h-full" src=${tracks[i].album.cover_medium} alt="" />
                    </div>

                    <div class="flex flex-col justify-center gap-1/2">
                        <p>${tracks[i].title}</p> 
                        
                        <div class="flex gap-2">
                            <p>${tracks[i].artist.name}</p>
                            <p>•</p>
                            <p>${tracks[i].album.title}</p>
                        </div>
                    </div>
                </div>

                <div class="loading-indicator hidden flex items-center gap-3">
                    <div class="relative block w-[35px] h-[35px] bg-conic from-[#fa0000] from-[75%] to-transparent to-[75%] rounded-full after:absolute after:inset-[3px] after:bg-white after:rounded-full"><div>
                </div>
            `;

            item.addEventListener("click", (e) => {
                download_track(item, tracks[i].id, tracks[i].title, tracks[i].artist.name, tracks[i].album.title, tracks[i].album.id, tracks[i].album.cover_xl);
            });

            res.querySelector(".tracks_results").appendChild(item);    
        }
    }

    const download_track = (element, deezer_id, title, artist, album, album_id, cover) => {
        if (downloading) {
            alert ("Wait for current download to finish!");
            return;
        }

        downloading = true;
        element.querySelector(".loading-indicator").classList.remove("hidden");

        fetch(`/download/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                id: yt_id,
                deezer_id : deezer_id,
                title: title,
                artist : artist,
                album: album,
                album_id: album_id,
                cover: cover
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status == "success") {
                const link = document.createElement("a");
                link.href = `${data.url}`.replace("website/", "");
                link.download = `${title} - ${artist}.mp3`;
                link.click();
            }
            else alert("Something Went Wrong");
        })
        .catch(e => {
            element.innerHTML = "";
            element.innerHTML = `
                <div class="flex items-center">
                    <div class="relative w-[60px] h-[60px] mr-3 aspect-square" >
                        <img class="w-full h-full" src="/static/img/error.png" alt="" />
                    </div>

                    <p class="text-lg font-[400]">Error Downloading Song Info</p>
                </div>
            `;
        })
        .finally(() => {
            downloading = false;
            element.querySelector(".loading-indicator").classList.add("hidden");            
        })
    }

    const download_track_blank = () => {
        if (downloading) {
            alert ("Wait for current download to finish!");
            return;
        }

        downloading = true;

        fetch(`/download-blank/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                id: yt_id
            })
        })
        .then(res => res.json())
        .then(data => {
            const link = document.createElement("a");
            link.href = `${data.url}`.replace("website/", "");
            link.download = `file.mp3`;
            link.click();

           downloading = false;
        })
    }

    res.addEventListener("click", () => open());
    res.querySelector(".search_result_btn_close").addEventListener("click", close);
    res.querySelector(".download_blank").addEventListener("click", download_track_blank)

    let timeout;
    let input = res.querySelector(".search_result_input");

    input.addEventListener("input", (e) => {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            search_tracks(e.target.value.trim());
        }, 500); // 500ms delay
    });
});

