document.addEventListener("DOMContentLoaded", function() {
    const submit = document.getElementById("submit");
    submit.addEventListener("click", function(event){
        insertWord();
    });
});

function setWordData(noteId){
    const word = document.getElementById("word").value;
    const meaning = document.getElementById("meaning").value;
    const note1 = document.getElementById("note1").value;
    const note2 = document.getElementById("note2").value;

    return {
        noteId: noteId,
        word: word,
        meaning: meaning,
        note1: note1,
        note2: note2
    }
}

function setExampleData(wordId) {
    const examples = document.getElementById("examples");
    const lines = examples.value.trim().split("\n").map(line => line.trim()).filter(line => line !== "");
    const result = [];

    for (let i = 0; i < lines.length; i += 3) {
        if (i + 2 < lines.length) {
            result.push({
                wordId: wordId,
                example: lines[i],
                hint: lines[i + 1],
                meaning: lines[i + 2],
                isCheck: false
            });
        }
    }

    return result;
}

function insertWord() {
    const params = new URLSearchParams(window.location.search);
    const noteId = params.get("noteId");
    if(!noteId) return;

    const word = setWordData(noteId);
    console.log(word);

    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/vocabulary/insert/word', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(word)
    })
    .then(response => response.json())
    .then(result => {
        const examples = setExampleData(result);
        insertExamples(examples);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}

function insertExamples(data) {
    console.log(data);
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/vocabulary/insert/word/example', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById("word").value = '';
        document.getElementById("meaning").value = '';
        document.getElementById("examples").value = '';
        document.getElementById("note1").value = '';
        document.getElementById("note2").value = '';
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}
