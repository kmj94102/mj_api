const container = document.getElementById('digimonInfoContainer');
const addBtn = document.getElementById('addBtn');
const saveBtn = document.getElementById('saveBtn');

let index = 1;

addBtn.addEventListener('click', () => {
  index++;
  const newGroup = document.createElement('div');
  newGroup.classList.add('digimonInfo');

  newGroup.innerHTML = `
    <img class="deleteBtn" src="close.svg" width="24px" height="24px">
    <div>이름</div>
    <input type="text" name="name">
    <div>오픈 여부</div>
    <input type="radio" name="isOpen-${index}" id="isOpenTrue-${index}">
    <label for="isOpenTrue-${index}">True</label>
    <input type="radio" name="isOpen-${index}" id="isOpenFalse-${index}">
    <label for="isOpenFalse-${index}">False</label>
  `;

  container.appendChild(newGroup);
});

container.addEventListener('click', (e) => {
  if (e.target.classList.contains('deleteBtn')) {
    const group = e.target.closest('.digimonInfo');
    if (group) {
      group.remove();
    }
  }
});

saveBtn.addEventListener('click', () => {
  const groupName = document.getElementById('group').value;
  const level = parseInt(document.getElementById('level').value);
  const isTranscend = document.getElementById('isTranscendTrue').checked;
  const groups = document.querySelectorAll('.digimonInfo');
  const list = [];

  groups.forEach((group, i) => {
    const name = group.querySelector('input[name="name"]').value.trim();
    const isOpen = group.querySelector('input[type="radio"]').checked;

    if(name && isOpen) {
      list.push({
        name: name,
        isOpen: isOpen,
        isTranscend: isTranscend,
        level: level
      });
    }

  });
  const data = {
    groupName: groupName,
    list: list
  };

  if (!groupName) {
    alert("그룹 이름을 입력해주세요.");
    return;
  }

  if (isNaN(level)) {
    alert("레벨 값이 올바르지 않습니다.");
    return;
  }

  if (list.length === 0) {
    alert("등록할 디지몬 정보가 없습니다.");
    return;
  }

  console.log('입력된 데이터:', data);

  fetch('http://127.0.0.1:8000/digimon/insert/dmo', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json'
       },
       body: JSON.stringify(data)
   })
   .then(response => response.json())
   .then(_ => {
      alert(groupName + ' 등록 성공');
   })
   .catch(error => {
      alert('등록 실패');
      console.error('Error:', error);
   });
});