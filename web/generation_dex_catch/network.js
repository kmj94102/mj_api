let selectName = '';
let selectNumber = '';
let selectIdx = '';

const fetchGeneration = async () => {
    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/dex/select/generation`);
    const data = await response.json();

    const generations = document.getElementById('title');
    data.forEach((item, index) => {
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.id = `radio-${index}`;
        radio.name = 'generations';
        radio.value = item.code;
        radio.addEventListener('change', handleRadioChange);

        const label = document.createElement('label');
        label.htmlFor = `radio-${index}`;
        label.textContent = item.name;

        generations.appendChild(radio);
        generations.appendChild(label);
    });
}

fetchGeneration()

async function fetchPokemonList() {
    const selectedRadio = document.querySelector('input[name="generations"]:checked');

    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/dex/select/list?generationIdx=${selectedRadio.value}`);
    const data = await response.json();

    const container = document.getElementById('container');
    container.replaceChildren();


    data.forEach((item, index) => {
        // 새 포켓몬 div 생성
        const pokemonDiv = document.createElement('div');
        pokemonDiv.className = 'pokemon';
        pokemonDiv.setAttribute('data-text', item.idx);
        if(item.isCatch) {
            pokemonDiv.style.backgroundColor = "#fafafa"
            pokemonDiv.style.color = "#17181D"
        } else {
            pokemonDiv.style.backgroundColor = "#17181D"
            pokemonDiv.style.color = "#fafafa"
        }

        // 이미지 추가
        const img = document.createElement('img');
        img.src = item.spotlight;
        img.alt = item.name;

        // 이름 추가
        const name = document.createElement('p');
        name.textContent = item.name;

        // 포켓몬 div에 추가
        pokemonDiv.appendChild(img);
        pokemonDiv.appendChild(name);

        pokemonDiv.addEventListener('click', () => {
            selectNumber = item.number;
            selectIdx = item.idx;
            selectName = item.name;
            openDialog();
        });

        // 컨테이너에 추가
        container.appendChild(pokemonDiv);
    });
}

function handleRadioChange(event) {
    fetchPokemonList();
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('close').addEventListener('click', closeDialog);

    document.getElementById('update').addEventListener('click', updateCatch);
});

async function openDialog() {
    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/pokemon/select/detail/${selectNumber}`);
    const data = await response.json();

    const evolution = document.getElementById('evolution');
    evolution.replaceChildren();

    const evolutionName = document.getElementById('evolution_name')
    evolutionName.textContent = selectName;

    data.evolutionInfo.forEach((item) => {
        const evolutionImages = document.createElement('div');
        evolutionImages.className = 'evolution_images';

        const beforeImg = document.createElement('img');
        beforeImg.src = item.beforeDot;
        beforeImg.className = 'evolution_image';

        const nextImg = document.createElement('img');
        nextImg.src = 'img_next.png'

        const afterImg = document.createElement('img');
        afterImg.src = item.afterDot;
        afterImg.className = 'evolution_image';

        evolutionImages.appendChild(beforeImg);
        evolutionImages.appendChild(nextImg);
        evolutionImages.appendChild(afterImg);

        const how_evolve = document.createElement('div');
        how_evolve.className = 'how_evolve';
        how_evolve.textContent = item.evolutionCondition;

        evolution.appendChild(evolutionImages);
        evolution.appendChild(how_evolve);
    });

    document.getElementById('dialog').style.display = 'block';
    document.getElementById('dialog-overlay').style.display = 'block';
}

function closeDialog() {
    document.getElementById('dialog').style.display = 'none';
    document.getElementById('dialog-overlay').style.display = 'none';
}

function updateCatch() {
    const dataToSend = {
        idx: selectIdx
    };

    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/dex/update/isCatch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        const items = document.getElementsByClassName('pokemon');
        const itemsArray = Array.from(items);
        const selectedPokemonItem = itemsArray.find(item => item.getAttribute('data-text') == selectIdx);
        if (selectedPokemonItem) {
            if (data) {
                selectedPokemonItem.style.backgroundColor = "#fafafa"
                selectedPokemonItem.style.color = "#17181D"
            } else {
                selectedPokemonItem.style.backgroundColor = "#17181D"
                selectedPokemonItem.style.color = "#fafafa"
            }
        }
        console.log(`${selectIdx} / ${data} / ${selectedPokemonItem} / ${itemsArray.length}`);
        closeDialog();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}