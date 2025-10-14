fetchCommunityInfo()
let dayOfWeek = '일요일';

document.addEventListener("DOMContentLoaded", async function() {
    const buttons = document.querySelectorAll('#weekday-container button');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('selected'));
            button.classList.add('selected');
            const selectedDay = button.dataset.day;
            dayOfWeek = selectedDay;
            console.log('선택된 요일:', selectedDay);
        });
    });

    const submit = document.getElementById('submit');
    submit.addEventListener('click', insertSchedule);

    const clear = document.getElementById('clear');
    clear.addEventListener('click', () => {
        document.getElementById('community').selectedIndex = 0;
        document.getElementById('rank'). value = "";
    });
});

function fetchCommunityInfo() {
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/persona/3/select/community', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        const community = document.getElementById('community');

        const defaultOption = document.createElement('option');
        defaultOption.value = 26;
        defaultOption.textContent = '커뮤선택';
        community.appendChild(defaultOption);

        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item['idx'];
            option.textContent = item['arcana'];
            community.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}

async function insertSchedule() {
    const month = document.getElementById('month').value;
    const day = document.getElementById('day').value;
    const title = document.getElementById('title').value;
    const contents = document.getElementById('contents').value;
    const communityIdx = document.getElementById('community').value;
    const rank = document.getElementById('rank').value;

    if(month < 0 || month > 12) {
        alert('월 확인 필요');
        return;
    }
    if(day < 0 || day > 31) {
        alert('일 확인 필요');
        return;
    }
    if(communityIdx != 26 && !rank) {
        alert('랭크 확인 필요');
        return;
    }

    const data = {
        month: month,
        day: day,
        dayOfWeek: dayOfWeek,
        title: title,
        contents: contents,
        communityIdx: communityIdx,
        rank: rank || 0,
        isComplete: false
    }

    fetch('http://127.0.0.1:8000/persona/3/insert/schedule', {
         method: 'POST',
         headers: {
             'Content-Type': 'application/json'
         },
         body: JSON.stringify(data)
     })
     .then(response => response.json())
     .then(_ => {
        alert(data.name + ' 등록 성공');
     })
     .catch(error => {
        alert('등록 실패');
        console.error('Error:', error);
     });
}