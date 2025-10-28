const rewardList = [
{id:1, name: 'EXP'},
{id:2, name: 'HP'},
{id:3, name: 'DS'},
{id:4, name: 'AT'},
{id:5, name: 'CT'},
{id:6, name: 'DE'},
{id:7, name: 'EV'},
{id:8, name: 'HT'},
{id:9, name: 'BL'},
{id:10, name: 'SCD'},
{id:11, name: '얼음 SCD'},
{id:12, name: '물 SCD'},
{id:13, name: '불 SCD'},
{id:14, name: '땅 SCD'},
{id:15, name: '바람 SCD'},
{id:16, name: '나무 SCD'},
{id:17, name: '빛 SCD'},
{id:18, name: '어둠 SCD'},
{id:19, name: '전기 SCD'},
{id:20, name: '강철 SCD'},
{id:21, name: '기본 SCD'},
{id:22, name: '데이터 SCD'},
{id:23, name: '바이러스 SCD'},
{id:24, name: '백신 SCD'},
{id:25, name: '언노운 SCD'},
];

let selectDigimonList = [];

document.querySelectorAll('.rewardType').forEach(select => {
    rewardList.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.name;
        select.appendChild(option);
    });
});

document.getElementById('searchButton').addEventListener('click', () => {
    const value = "%" + document.getElementById('searchValue').value + "%";
    const data = {name: value};

    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/digimon/select/search/dmo', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json'
       },
       body: JSON.stringify(data)
   })
   .then(response => response.json())
   .then(data => {
      const searchResult = document.getElementById('search_result');
      searchResult.innerHTML = '';

      data.forEach(item => {
        searchResult.insertAdjacentHTML('beforeend', `
          <div class="select_result_item" style="width: auto;" data-index="${item['digimonId']}">
            <span>${item.groupName}</span>
            <span>${item.digimonName}</span>
          </div>
        `);
      });
   })
   .catch(error => {
      alert('조회 실패');
      console.error('Error:', error);
   });

});

 document.getElementById('search_result').addEventListener('click', e => {
  const div = e.target.closest('.select_result_item');
  if (!div) return;

  const digimonId = parseInt(div.dataset.index);
  const spans = div.querySelectorAll('span');
  const groupName = spans[0]?.textContent.trim();
  const digimonName = spans[1]?.textContent.trim();

  if (groupName && digimonName) {
    console.log('선택된 그룹:', groupName);
    console.log('선택된 디지몬:', digimonName);

    selectDigimonList.push({groupName: groupName, digimonName: digimonName, digimonId: digimonId});
    updateSelectList();
  }
});

document.getElementById('select_list').addEventListener('click', e => {
    const span = e.target.closest('.select_digimon');
    if (!span) return;

    const targetName = span.textContent.trim();
    console.log(targetName);
    selectDigimonList = selectDigimonList.filter(item => item.digimonName !== targetName);
    updateSelectList();
});

function updateSelectList() {
    const selectList = document.getElementById('select_list');
    selectList.innerHTML = '';
    selectDigimonList.forEach(item => {
        selectList.insertAdjacentHTML('beforeend',
        `<span class="select_digimon">${item['digimonName']}</span>`
      )
    });
}

document.getElementById('register').addEventListener('click', e=> {
    const unionName = document.getElementById('union_name').value;

    const digimonRewardValue = parseInt(document.getElementById('digimonRewardValue').value);
    const digimonRewardType = document.getElementById('digimonRewardType').value;
    const levelRewardValue = parseInt(document.getElementById('levelRewardValue').value);
    const levelRewardType = document.getElementById('levelRewardType').value;
    const transcendRewardValue = parseInt(document.getElementById('transcendRewardValue').value);
    const transcendRewardType = document.getElementById('transcendRewardType').value;
    const lastLevelRewardValue = parseInt(document.getElementById('lastLevelRewardValue').value);
    const lastLevelRewardType = document.getElementById('lastLevelRewardType').value;

    const level = parseInt(document.getElementById('level').value);
    const lastLevel = parseInt(document.getElementById('lastLevel').value);
    const length = selectDigimonList.length;

    const rewardNConditions = [
        {rewardType: rewardList[digimonRewardType].id, rewardValue: digimonRewardValue, conditionType: 1, conditionValue: length},
        {rewardType: rewardList[levelRewardType].id, rewardValue: levelRewardValue, conditionType: 2, conditionValue: level},
        {rewardType: rewardList[transcendRewardType].id, rewardValue: transcendRewardValue, conditionType: 3, conditionValue: length},
        {rewardType: rewardList[lastLevelRewardType].id, rewardValue: lastLevelRewardValue, conditionType: 4, conditionValue: lastLevel},
    ];

    const digimonList = selectDigimonList.map(item => ({
        digimonId: item.digimonId
    }));

    const data = {
        unionName: unionName,
        rewardNConditions: rewardNConditions,
        digimonList: digimonList
    }

      fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/digimon/insert/dmo/union', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json'
       },
       body: JSON.stringify(data)
   })
   .then(response => response.json())
   .then(_ => {
      alert(unionName + ' 등록 성공');
   })
   .catch(error => {
      alert('등록 실패');
      console.error('Error:', error);
   });
});