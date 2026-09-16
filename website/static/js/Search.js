const searchBar = document.getElementById("search_input");
const cat_btns = document.querySelectorAll(".cat_btn");
const cat_sections = document.querySelectorAll(".cat_section");

let current_cat = 0;
let timeout;

searchBar.addEventListener("input", (e) => {
    clearTimeout(timeout);

    timeout = setTimeout(() => {
        search(e.target.value.trim());
    }, 500); // 500ms delay
});

for (let i = 0; i < cat_btns.length; i++) {
    cat_btns[i].addEventListener("click", () => {
        cat_btns.forEach(btn => btn.classList.remove("bg-red-400"));
        cat_sections.forEach(btn => btn.classList.add("hidden"));

        cat_btns[i].classList.add("bg-red-400");
        cat_sections[i].classList.remove("hidden");

        current_cat = i;
    });
}

const search = (query) => {
    if (query.length < 1) return;
        
    fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            q: query
        })
    })
    .then(res => res.json())
    .then(data => {
        render_data(data);
    })
    .catch(e => {
        console.log(e);
    })
}

const render_data = (data) => {
    // Tracks
    const tracks_parent = document.getElementById("tracks_parent");
    tracks_parent.innerHTML = "";

    data.tracks.forEach((track) => {
        let e = document.createElement("div");
        e.className = "relative flex items-center justify-between px-2 py-1 hover:bg-white/20 rounded-lg overflow-hidden";

        e.addEventListener('click', () => {
            loadSongWithId(track.id);
        });
        
        e.innerHTML = `
            <div class="flex items-center gap-2">
                <div class="w-[50px] h-[50px] aspect-square shrink-0 rounded-md overflow-hidden"><img class="w-full h-full" src="${ track.album.cover_big }" alt="${ track.title }"></div>
                <div class="overflow-hidden whitespace-nowrap w-[75%] overflow-hidden">
                    <p class="truncate text-[15px] font-[500]">${ track.title }</p>
                    <p class="truncate text-[12px] -mt-[2px]">${ track.artist.name }</p>
                </div>
            </div>

            <div class="flex gap-3 text-white/90">
                <button class="w-[25px] h-[25px] p-[4px] rounded-full cursor-pointer"><i class="w-full h-full" data-lucide="ellipsis"></i></button>
            </div>
        `;
        
        tracks_parent.appendChild(e);
    })

    // Artists
    const artists_parent = document.getElementById("artists_parent");
    artists_parent.innerHTML = "";

    data.artists.forEach((artist) => {
        let e = document.createElement("div");
        
        e.innerHTML = `
            <a href="/artist/${artist.id}" class="flex items-center gap-2 md:px-2 py-1 hover:bg-white/20 rounded-lg overflow-hidden">
                <div class="w-[50px] h-[50px] aspect-square shrink-0 rounded-full overflow-hidden"><img class="w-full h-full" src="${ artist.picture_big }" alt="${ artist.name }"></div>
                <div class="overflow-hidden whitespace-nowrap w-[75%] overflow-hidden">
                    <p class="truncate text-[15px] font-[500] -mt-[2px]">${ artist.name }</p>
                </div>
            </a>
        `;
        
        artists_parent.appendChild(e);
    })

    // Albums
    const albums_parent = document.getElementById("albums_parent");
    albums_parent.innerHTML = "";

    data.albums.forEach((album) => {
        let e = document.createElement("div");
        
        e.innerHTML = `
            <a href="/album/${album.id}" class="flex items-center gap-2 md:px-2 py-1 hover:bg-white/20 rounded-lg overflow-hidden">
                <div class="w-[50px] h-[50px] aspect-square shrink-0 rounded-md overflow-hidden"><img class="w-full h-full" src="${ album.cover_big }" alt="${ album.title }"></div>
                <div class="overflow-hidden whitespace-nowrap w-[75%] overflow-hidden">
                    <p class="truncate text-[15px] font-[500]">${ album.title }</p>
                    <p class="truncate text-[12px] -mt-[2px]">${ album.artist.name }</p>
                </div>
            </a>
        `;
        
        albums_parent.appendChild(e);
    })

    lucide.createIcons();
}