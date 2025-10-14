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
    <input type="text" id="name">
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
  const groups = document.querySelectorAll('.digimonInfo');
  const data = [];

  groups.forEach((group, i) => {
    const example = group.querySelector('input[name="example"]').value.trim();
    const meaning = group.querySelector('input[name="meaning"]').value.trim();
    const hint = group.querySelector('input[name="hint"]').value.trim();
    const selected = group.querySelector('input[type="radio"]').checked;

    data.push({
      id: i + 1,
      example,
      meaning,
      hint,
      selected
    });
  });

  console.log('입력된 데이터:', data);
  alert(`총 ${data.length}개의 항목 중 선택된 항목: ${data.find(d => d.selected)?.id || '없음'}`);
});