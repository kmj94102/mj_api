const rewardList = [
{id:1, name: 'EXP'},
{id:2, name: 'HP'},
{id:3, name: 'DS'},
{id:4, name: 'AT'},
{id:5, name: 'CT'},
{id:5, name: 'DE'},
{id:6, name: 'EV'},
{id:7, name: 'HT'},
{id:8, name: 'BL'},
{id:9, name: 'SCD'},
{id:10, name: '얼음 SCD'},
{id:11, name: '물 SCD'},
{id:12, name: '불 SCD'},
{id:13, name: '땅 SCD'},
{id:14, name: '바람 SCD'},
{id:15, name: '나무 SCD'},
{id:16, name: '빛 SCD'},
{id:17, name: '어둠 SCD'},
{id:18, name: '전기 SCD'},
{id:19, name: '강철 SCD'},
{id:20, name: '기본 SCD'},
{id:21, name: '데이터 SCD'},
{id:22, name: '바이러스 SCD'},
{id:23, name: '백신 SCD'},
{id:24, name: '언노운 SCD'},
];


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
      data.forEach(item => {
            const digimonName = item['digimonName'];
            const groupName = item['groupName'];
            const digimonId = item['digimonId'];
            console.log("digimonName: " + digimonName + " groupNam: " + groupName);
        });
   })
   .catch(error => {
      alert('조회 실패');
      console.error('Error:', error);
   });

});