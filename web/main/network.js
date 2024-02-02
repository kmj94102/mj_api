const fetchData = async () => {
    const response = await fetch(`https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/web/select`);
    const data = await response.json();
    console.log(data);
}

function goToPage(link) {
    window.location.href = link;
}

fetchData();