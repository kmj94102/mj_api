const pokemonList = document.getElementById('pokemon-list');

let isLoading = false;
let currentPage = 0;
let generate = "";
let selectNumber = '';

const fetchData = async () => {
    isLoading = true;

    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/pokemon/select/list?skip=${currentPage * 100}&limit=100&generation=${generate}`);
    const data = await response.json();
    console.log(currentPage);
    const pokemonName = document.getElementById('pokemonName');
    const infoDialog = document.getElementById('infoDialog');

    data.list.forEach((pokemon, index) => {
        const item = document.createElement('div');
        item.className = 'pokemon-item';
        item.setAttribute('data-text', pokemon.number);
        if (pokemon.isCatch) {
            item.style.backgroundColor = "#fafafa"
            item.style.color = "#17181D"
        } else {
            item.style.backgroundColor = "#17181D"
            item.style.color = "#fafafa"
        }

        const imageDiv = document.createElement('div');
        imageDiv.className = 'images';

        const image = document.createElement('img');
        image.src = pokemon.image;

        const shinyImage = document.createElement('img');
        shinyImage.src = pokemon.shinyImage;

        imageDiv.appendChild(image);
        imageDiv.appendChild(shinyImage);

        const name = document.createElement('div');
        name.className = 'name'
        name.innerHTML = pokemon.number + '<br>' + pokemon.name;

        item.appendChild(imageDiv);
        item.appendChild(name);
        item.addEventListener("click", function () {
            infoDialog.style.display = 'block';
            pokemonName.innerText = pokemon.name;
            selectNumber = pokemon.number;
        });

        pokemonList.appendChild(item);
    });

    isLoading = false;
    currentPage++;
};

const handleScroll = () => {
    if (isLoading) return;

    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
        fetchData();
    }
};

window.addEventListener('scroll', handleScroll);

// Load initial data
fetchData();

function openDialog() {
    var dialog = document.getElementById("dialog");
    dialog.classList.add("show-dialog");
}

function closeDialog() {
    var dialog = document.getElementById("dialog");
    dialog.classList.remove("show-dialog");
}

document.addEventListener("DOMContentLoaded", function () {
    const menu = document.getElementById("menu");
    menu.addEventListener("click", openDialog);

    const divs = document.querySelectorAll('.generate');

    divs.forEach(div => {
        div.addEventListener('click', () => {
            divs.forEach(d => d.classList.remove('selected'));
            div.classList.add('selected');
            const select = div.dataset.info;
            if (generate != select) {
                generate = select;
                currentPage = 0;
                pokemonList.innerHTML = '';
                fetchData();
            }

            closeDialog();
        });
    });
});

function sendData(choice) {
    const infoDialog = document.getElementById('infoDialog');
    infoDialog.style.display = 'none';
   
    updateCatchStatus(choice);
}

function updateCatchStatus(isCaught) {
    const dataToSend = {
        number: selectNumber,
        isCatch: isCaught
    };

    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/pokemon/update/catch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
        const items = document.getElementsByClassName('pokemon-item');
        const itemsArray = Array.from(items);

        const selectedPokemonItem = itemsArray.find(item => item.getAttribute('data-text') === selectNumber);
        if (selectedPokemonItem) {
            if (isCaught) {
                selectedPokemonItem.style.backgroundColor = "#fafafa"
                selectedPokemonItem.style.color = "#17181D"
            } else {
                selectedPokemonItem.style.backgroundColor = "#17181D"
                selectedPokemonItem.style.color = "#fafafa"
            }
        } else {
            console.log('해당 number 값을 가진 포켓몬을 찾을 수 없습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });

    infoDialog.style.display = 'none';
}