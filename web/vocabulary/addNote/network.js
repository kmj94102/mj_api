document.addEventListener("DOMContentLoaded", function() {
    const submit = document.getElementById("submit");

    submit.addEventListener("click", function(event){
        insertNote();
    });
});

function insertNote() {
    const language = document.querySelector('input[name="language"]:checked')?.value;
    console.log(language);

    const now = new Date();
    const fixedTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 7, 0, 0);

    const timestamp = fixedTime.getTime();
    console.log(timestamp);

    const title = document.getElementById("title").value;
    console.log(title);

    const dataToSend = {
        title: title,
        language: language,
        timestamp: timestamp
    };
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/vocabulary/insert/note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        console.log(`data: ${dataToSend.year}/${dataToSend.month}`);
        console.log('Server response:', data);
        alert(data);
        history.back();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`);
    });
}