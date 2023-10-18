const pokemonList = document.getElementById('pokemon-list');

let isLoading = false;
let currentPage = 0;
let generate = "";

const fetchData = async () => {
    isLoading = true;

    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/pokemon/select/list?skip=${currentPage * 100}&limit=100&generation=${generate}`);
    const data = await response.json();
    console.log(currentPage);

    data.list.forEach(pokemon => {
        const item = document.createElement('div');
        item.className = 'pokemon-item';
        item.setAttribute('data-text', pokemon.isCatch);
        if(pokemon.isCatch) {
            item.style.backgroundColor = "#fafafa"
            item.style.color = "#17181"
        } else {
            item.style.backgroundColor = "#17181"
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

//        const button = document.createElement('div');
//        button.innerText = "업데이트"
//        button.addEventListener("click", function() {
//          // 클릭 시 실행될 코드를 작성합니다.
//          alert(`${pokemon.name}가 클릭되었습니다!  ${pokemon.number}`);
//        });


        item.appendChild(imageDiv);
        item.appendChild(name);
//        item.appendChild(button);

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

document.addEventListener("DOMContentLoaded", function() {
    const menu = document.getElementById("menu");
    menu.addEventListener("click", openDialog);

    const divs = document.querySelectorAll('.generate');

    divs.forEach(div => {
      div.addEventListener('click', () => {
        divs.forEach(d => d.classList.remove('selected'));
        div.classList.add('selected');
        const select = div.dataset.info;
        if(generate != select) {
            generate = select;
            currentPage = 0;
            pokemonList.innerHTML = '';
            fetchData();
        }

        closeDialog();
      });
    });
});