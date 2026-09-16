let audio = new Audio();
let isPlaying = false;

// Play actions
const playBtns = document.querySelectorAll(".play-button");
const prevBtns = document.querySelectorAll('.prev-button');
const nextBtns = document.querySelectorAll(".next-button");

// Title & Artist
const titleTexts = document.querySelectorAll(".title-text");
const artistTexts = document.querySelectorAll(".artist-text");

// Art
const songArt = document.querySelectorAll(".current-song-art");

// Time
const currentTime = document.querySelectorAll('.elapsed-time');
const totalTime = document.querySelectorAll('.total-time');

// Progress
const progressContainer = document.querySelectorAll(".song-progress-bar");

// Queue
let queueOpen = false;
const queue_btn = document.getElementById("queue_btn");
const queue_fs = document.getElementById("queue_fs")

// #region Play/Pause
audio.addEventListener("play", playSong);
audio.addEventListener('pause', pauseSong);

playBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        if (!audio.src) return;
        isPlaying ? pauseSong() : playSong();
    });
});

function playSong() {
    audio.play();
    isPlaying = true;

    playBtns.forEach(btn => {
        btn.classList.remove("pause")
    });
    
    document.querySelectorAll(".now-palying-icon-bar").forEach(bar => {
        bar.classList.remove("paused");
    });
}

function pauseSong() {
    audio.pause();
    isPlaying = false;
    
    playBtns.forEach(btn => {
        btn.classList.add("pause")
    });

    document.querySelectorAll(".now-palying-icon-bar").forEach(bar => {
        bar.classList.add("paused");
    });
}
// #endregion

// #region Progress bar
audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
        const progress = (audio.currentTime / audio.duration) * 100;

        progressContainer.forEach(container => {
            container.querySelector("div").style.width = `${progress}%`;
        });

        currentTime.forEach(time => {
            time.innerHTML = formatTime(audio.currentTime);
        });
        
        totalTime.forEach(time => {
            time.innerHTML = formatTime(audio.duration);
        });
    }
});

progressContainer.forEach(container => {
    container.addEventListener('click', (e) => {
        const width = container.clientWidth;
        const clickX = e.offsetX;
        const duration = audio.duration;
        audio.currentTime = (clickX / width) * duration;
    });
});

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}
// #endregion

// #region Full Screen
const open_player = document.getElementById("open_player");
const close_player = document.getElementById("exit_btn");

const fullscreen_player = document.getElementById("f_player");
const player_info = document.getElementById("player_fs");

open_player.addEventListener("click", () => {
    fullscreen_player.classList.replace("hidden", "fixed");
    document.querySelector("body").classList.add("overflow-hidden");
})

close_player.addEventListener("click", () => {
    fullscreen_player.classList.replace("fixed", "hidden");
    document.querySelector("body").classList.remove("overflow-hidden");
})

queue_btn.addEventListener("click", () => {
    player_info.classList.toggle("minimize");
    queue_btn.classList.toggle("open");
})
// #endregion

// #region Track Option
const items = document.querySelectorAll(".song_item");
const opt_screen = document.getElementById("opt_screen");

opt_screen.addEventListener("click", () => {
    opt_screen.classList.replace("fixed", "hidden");
    document.querySelector("body").classList.remove("overflow-hidden");
})

opt_screen.querySelector("div").addEventListener("click", (e) => {
    e.stopPropagation()
})

items.forEach(item => {
    const id = item.getAttribute("data-id");
    item.addEventListener("click", () => {
        loadSongWithId(id);
    })

    const option_btn = item.querySelector(".option_btn")
    option_btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        
        const response = await fetch(`/track_info/${id}`);
        const data = await response.json();

        if(data.status == "success") {
            opt_screen.setAttribute("data-id", data.track.id)

            opt_screen.querySelector("img").setAttribute("src", data.track.album.cover_xl);
            opt_screen.querySelector(".opt_title").innerHTML = data.track.title;
            opt_screen.querySelector(".opt_artist").innerHTML = data.track.artist.name;

            opt_screen.classList.replace("hidden", "fixed");
            document.querySelector("body").classList.add("overflow-hidden");
        }

        document.getElementById("like_btn").addEventListener("click", like_clicked)
    })
})

function like_clicked(e) {
    let id = opt_screen.getAttribute("data-id");

    fetch("/library/like_song", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            id: id
        })
    })
    .then(res => res.json())
    .then(data => {
        let i = e.target.querySelector('svg');
        let p = e.target.querySelector('p');
        
        if (data.liked) {
            i.classList.add("fill-red-500", "stroke-red-500");
            p.innerHTML = "Remove from liked songs";
        }
        else {
            i.classList.remove("fill-red-500", "stroke-red-500");
            p.innerHTML = "Liked Song";
        }

        console.log(data);
    })
}
// #endregion

// #region Load Song
async function loadSongWithId(id) {
    const response = await fetch(`/track/${id}`);
    const data = await response.json();

    if (!data) return false;

    audio.src = data.preview;

    navigator.mediaSession.metadata = new MediaMetadata({
        title: data.title,
        artist: data.artist.name,
        album: data.album.title,
        artwork: [
            {
                src: data.album.cover_xl,
                sizes: "1000x1000",
                type: "image/png"
            }
        ]
    });

    titleTexts.forEach(txt => txt.innerHTML = data.title);
    artistTexts.forEach(txt => {
        txt.innerHTML = data.artist.name;
        txt.setAttribute("href", `/artist/${data.artist.id}`);
    });
    songArt.forEach(art => {
        art.setAttribute("src", data.album.cover_xl);
        art.setAttribute("alt", `${data.title} Cover Art`);
    });

    playSong();
    highlightSong(data.id)
    scrollText();
} 

function highlightSong(id) {
    items.forEach(item => {
        if (item.getAttribute("data-id") == id) {
            item.classList.add("text-red-400");
            return;
        }
        else item.classList.remove("text-red-400");
    })
}
// #endregion

// #region Text Scroll
function scrollText() {
    titleTexts.forEach(txt => {
        const overflow = txt.scrollWidth > txt.parentElement.clientWidth;

        if (overflow) txt.classList.add('scroll');
        else txt.classList.remove('scroll');
    });
    
    artistTexts.forEach(txt => {
        const overflow = txt.scrollWidth > txt.parentElement.clientWidth;

        if (overflow) txt.classList.add('scroll');
        else txt.classList.remove('scroll');
    });
}

scrollText();
// #endregion

// #region Mobile Navbar
let activeLink;
const mobileNavLinks = document.querySelectorAll(".mobile-nav-link");
const highlight = document.querySelector(".mobile-nav-link-highlight");

for (let i = 0; i < mobileNavLinks.length; i++) {
    mobileNavLinks[i].addEventListener('click', (e) => {
        // e.preventDefault();

        activeLink = i;
        highlightNavItem(i);
    });
}

function highlightNavItem(i) {
    mobileNavLinks.forEach(link => link.classList.remove("text-red-400"));
    mobileNavLinks[i].classList.add("text-red-400");

    highlight.style.width = `${mobileNavLinks[i].offsetWidth}px`;
    highlight.style.height = `${mobileNavLinks[i].offsetHeight}px`;
    highlight.style.left = `${mobileNavLinks[i].offsetLeft}px`;
    highlight.style.top = `${mobileNavLinks[i].offsetTop}px`;
}
// #endregion





