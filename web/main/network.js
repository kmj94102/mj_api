const fetchData = async () => {
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/webApi/select', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
        const container = document.getElementById('container');
        data.forEach(cardData => {
          const card = createCard(cardData.name, cardData.address);
          container.appendChild(card);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}

function createCard(title, link) {
      const cardDiv = document.createElement('div');
      cardDiv.className = 'card';
      cardDiv.textContent = title;
      cardDiv.onclick = function() {
        goToPage(link);
      };

  return cardDiv;
}

function goToPage(link) {
    window.location.href = link;
}

fetchData();