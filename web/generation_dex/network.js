let selectIndex = 0;
let selectNumber = '';
let selectName = '';

const fetchGeneration = async () => {
    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/dex/select/generation`);
    const data = await response.json();

    const generations = document.getElementById('generation');
    data.forEach((item, index) => {
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.id = `radio-${index}`;
        radio.name = 'generations';
        radio.value = item.code;

        const label = document.createElement('label');
        label.htmlFor = `radio-${index}`;
        label.textContent = item.name;

        generations.appendChild(radio);
        generations.appendChild(label);
    });
}

fetchGeneration()

async function fetchSearchPokemonList() {
    const item = document.getElementById('search_input');
    const selectImg = document.getElementById('select_img');

    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/pokemon/select/list?name=${item.value}&skip=0&limit=100`);
    const data = await response.json();

    const searchResult = document.getElementById('search_result');
    searchResult.replaceChildren();

    data.list.forEach((item, index) => {
        const img = document.createElement('img');
        img.src = item.spotlight;
        img.classList.add('result');

        img.addEventListener('click', () => {
            selectImg.src = item.spotlight;
            selectIndex = item.index;
            selectNumber = item.number;
            selectName = item.name;
        });

        searchResult.appendChild(img);
    })
}

async function fetchSearchPokemon(number) {
    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/pokemon/select?number=${number}`);
    const data = await response.json();

    const selectImg = document.getElementById('select_img');
    selectImg.src = data.spotlight;
    selectIndex = data.index;
    selectNumber = data.number;
    selectName = data.name;
}

async function sendData() {
    const selectedRadio = document.querySelector('input[name="generations"]:checked');
    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/dex/insert?pokemonIdx=${selectIndex}&generationIdx=${selectedRadio.value}&name=${selectName}`);
    const data = await response.json();
    alert(data);
}

document.addEventListener("DOMContentLoaded", function () {
    const search_button = document.getElementById("search_button");
    search_button.addEventListener("click", fetchSearchPokemonList);

    const before = document.getElementById("before");
    before.addEventListener("click", () => {
        if(selectNumber != null) {
            let num = parseInt(selectNumber, 10) - 1;
            if(num <= 0) return;

            let newStrNum = num.toString().padStart(4, '0');
            fetchSearchPokemon(newStrNum)
        }
    });

    const next = document.getElementById("next");
    next.addEventListener("click", () => {
        if(selectNumber != null) {
            let num = parseInt(selectNumber, 10) + 1;
            let newStrNum = num.toString().padStart(4, '0');
            fetchSearchPokemon(newStrNum)
        }
    });

    const submit = document.getElementById("submit");
    submit.addEventListener("click", sendData);
});