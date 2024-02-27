var teamList = [];
var selectedTeams = [];

const fetchData = async () => {
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/purchase/select/teamList', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
        teamList = data;
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}

fetchData()

function selectTeams() {
    // 랜덤으로 2개의 팀 선택
    selectedTeams = selectRandomTeams(teamList);

    // 선택된 팀들을 화면에 표시
    displayTeams(selectedTeams);
}

function selectRandomTeams(teamList) {
    const selectedTeams = [];
    while (selectedTeams.length < 2) {
        const randomIndex = Math.floor(Math.random() * teamList.length);
        const selectedTeam = teamList[randomIndex];
        if (!selectedTeams.includes(selectedTeam)) {
            selectedTeams.push(selectedTeam);
        }
    }
    return selectedTeams;
}

function displayTeams(teams) {
    const teamResultDiv = document.getElementById("teamResult");
    teamResultDiv.innerHTML = ""; // 이전에 표시된 내용 제거
    const teamListElement = document.createElement("ul");
    teams.forEach(team => {
        const teamItem = document.createElement("li");
        teamItem.textContent = team["name"];
        teamListElement.appendChild(teamItem);
    });
    teamResultDiv.appendChild(teamListElement);
}

document.addEventListener("DOMContentLoaded", function() {
    const register = document.getElementById("register")
    register.addEventListener('click', insertGame)
});

function insertGame() {
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;
    const dateTime = `${date}T${time}:00.000Z`

    if(date === '') {
        alert("날짜를 선택해주세요")
    }

    if(selectedTeams.length < 2) {
        alert("팀 선택을 눌러주세요");
    }

    const data = {
        gameDate: dateTime,
        leftTeamId:selectedTeams[0]["teamId"],
        rightTeamId:selectedTeams[1]["teamId"]
    }

    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/purchase/insert/game', {
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