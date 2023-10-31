document.addEventListener("DOMContentLoaded", function() {
    const searchButton = document.getElementById('search');
    const searchImage = document.getElementById('searchImage');
    const register = document.getElementById('register');

    const image = document.getElementById('image');
    const shinyImage = document.getElementById('shinyImage');
    const spotlight = document.getElementById('spotlight');
    const shinySpotlight = document.getElementById('shinySpotlight');

    image.addEventListener('input', setImage);
    shinyImage.addEventListener('input', setShinyImage);
    spotlight.addEventListener('input', setSpotlight);
    shinySpotlight.addEventListener('input', setShinySpotlight);

    searchButton.addEventListener('click', pokemonInfoSearch);
    searchImage.addEventListener('click', pokemonImageSearch);
    register.addEventListener('click', insertPokemon)
});

function setImage() {
    const image = document.getElementById('image');
    const viewImage = document.getElementById('viewImage');
    viewImage.src = image.value;
};

function setShinyImage() {
    const shinyImage = document.getElementById('shinyImage');
    const viewShinyImage = document.getElementById('viewShinyImage');
    viewShinyImage.src = shinyImage.value;
}

function setSpotlight() {
    const spotlight = document.getElementById('spotlight');
    const viewSpotlight = document.getElementById('viewSpotlight');
    viewSpotlight.src = spotlight.value;
}

function setShinySpotlight() {
    const shinySpotlight = document.getElementById('shinySpotlight');
    const viewShinySpotlight = document.getElementById('viewShinySpotlight');
    viewShinySpotlight.src = shinySpotlight.value;
}

async function pokemonInfoSearch() {
    const search_number = document.getElementById('search_number');
    const classification = document.getElementById('classification');
    const name = document.getElementById('name');
    const status = document.getElementById('status');
    const description = document.getElementById('description');
    const number = document.getElementById('number');
    const attribute = document.getElementById('attribute');
    const characteristic = document.getElementById('characteristic');
    const engName = document.getElementById('engName');

    number.value = String(search_number.value).padStart(4, '0');

    getPokemonDataById(search_number.value)
      .then(pokemonData => {
        // 스테이터스 설정
        const statusList = pokemonData["stats"].map(item=>{
            return item["base_stat"];
        });
        status.value = statusList.join(",");

        pokemonData["types"].map(async item => {
          return await getPokemonTypes(item["type"]["url"])
            .then(result => {
                if(!attribute.value) {
                    attribute.value = result["names"].find(item => item["language"]["name"] === "ko")["name"];
                } else {
                    attribute.value += "," + result["names"].find(item => item["language"]["name"] === "ko")["name"];
                }
            });
        });

        pokemonData["abilities"].map(async item => {
          return await getPokemonCharacteristic(item["ability"]["url"])
            .then(result => {
                if(!characteristic.value) {
                    characteristic.value = result["names"].find(item => item["language"]["name"] === "ko")["name"];
                } else {
                    characteristic.value += "," + result["names"].find(item => item["language"]["name"] === "ko")["name"];
                }
            });
        });

      });

    getPokemonSpeciesById(search_number.value)
        .then(info => {
            classification.value = info["genera"].find(item => item["language"]["name"] === "ko")["genus"];
            name.value = info["names"].find(item => item["language"]["name"] === "ko")["name"];
            engName.innerText = info["names"].find(item => item["language"]["name"] === "en")["name"];
            description.value = info["flavor_text_entries"].find(item => item["language"]["name"] === "ko")["flavor_text"];
        });
}

function getPokemonDataById(id) {
  const url = `https://pokeapi.co/api/v2/pokemon/${id}/`;

  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      return data; // 데이터 반환
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
}

function getPokemonSpeciesById(id) {
  const url = `https://pokeapi.co/api/v2/pokemon-species/${id}/`;

  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      return data; // 데이터 반환
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
}

async function getPokemonTypes(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data; // 데이터 반환
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
    return null; // 에러 발생 시 반환할 값
  }
}

async function getPokemonCharacteristic(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data; // 데이터 반환
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
    return null; // 에러 발생 시 반환할 값
  }
}

 function pokemonImageSearch() {
    const search_number = document.getElementById('search_number');
    const number = document.getElementById('number');

    const image = document.getElementById('image');
    const shinyImage = document.getElementById('shinyImage');
    const spotlight = document.getElementById('spotlight');
    const shinySpotlight = document.getElementById('shinySpotlight');

    image.value = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${search_number.value}.png`
    shinyImage.value = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/shiny/${search_number.value}.png`
    spotlight.value = `https://firebasestorage.googleapis.com/v0/b/mbank-2a250.appspot.com/o/${number.value}.png?alt=media&token=1d71a0d9-28aa-410a-9694-d76a29e327f5`
    shinySpotlight.value = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/${search_number.value}.png`

    const event = new Event('input');
    image.dispatchEvent(event);
    shinyImage.dispatchEvent(event);
    spotlight.dispatchEvent(event);
    shinySpotlight.dispatchEvent(event);
 }

 function insertPokemon() {
    const number = document.getElementById('number');
    const name = document.getElementById('name');
    const status = document.getElementById('status');
    const classification = document.getElementById('classification');
    const characteristic = document.getElementById('characteristic');
    const attribute = document.getElementById('attribute');
    const image = document.getElementById('image');
    const shinyImage = document.getElementById('shinyImage');
    const spotlight = document.getElementById('spotlight');
    const shinySpotlight = document.getElementById('shinySpotlight');
    const description = document.getElementById('description');
    const generation = document.getElementById('generation');

    const data = {
        index: 0,
        number: number.value,
        name: name.value,
        status: status.value,
        classification: classification.value,
        characteristic: characteristic.value,
        attribute: attribute.value,
        image: image.value,
        shinyImage: shinyImage.value,
        spotlight: spotlight.value,
        shinySpotlight: shinySpotlight.value,
        description: description.value,
        generation: parseInt(generation.value),
        isCatch: false
    }

    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/pokemon/insert', {
         method: 'POST',
         headers: {
             'Content-Type': 'application/json'
         },
         body: JSON.stringify(data)
     })
     .then(response => response.json())
     .then(data => {
        alert(data);
        console.log(data);
     })
     .catch(error => {
        alert('등록 실패');
        console.error('Error:', error);
     });
 }