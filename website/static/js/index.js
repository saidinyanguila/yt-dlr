const results = document.querySelectorAll(".search_result");

const download_status = document.getElementById("download_status");
const download_status_title = document.getElementById("download_status_title");
const download_status_artist = document.getElementById("download_status_artist");
const download_status_img = document.getElementById("download_status_img");

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

        for (let i = 0; i < 5; i++) {
            if (!tracks[i]) return;

            let item = document.createElement("div");
            item.className = "relative mb-1 flex items-center py-1 px-3";
            
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
        download_status.classList.remove("hidden"); 
        download_status.querySelector(".loading-bar").classList.remove("hidden");

        download_status.classList.replace("-bottom-[100%]", "bottom-0")
        download_status_title.innerHTML = title;
        download_status_artist.innerHTML = artist;
        download_status_img.setAttribute("src", cover);

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
            download_status.querySelector(".status_text").innerHTML = "Done!";
            download_status.querySelector(".loading-bar").classList.add("hidden");

            setTimeout(() => {
                download_status.classList.replace("bottom-0", "-bottom-[100%]"); 
                
                setTimeout(() => {
                    download_status.classList.add("hidden"); 
                }, 3500);   
            }, 3500);       
        })
    }

    const download_track_blank = (element) => {
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
    
    const blank_btn = res.querySelector(".download_blank");
    blank_btn.addEventListener("click", () => download_track_blank(blank_btn));
    
    let timeout;
    let input = res.querySelector(".search_result_input");

    input.addEventListener("input", (e) => {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            search_tracks(e.target.value.trim());
        }, 500); // 500ms delay
    });
});

// Date
const date = new Date();
document.getElementById("cr_text").innerHTML = `YT Downloader &copy${date.getFullYear()}`;