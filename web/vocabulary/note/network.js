document.addEventListener("DOMContentLoaded", function() {
    const newVocabulary = document.getElementById("newVocabulary");

    newWord.addEventListener("click", function(event){
        window.location.href = '../addWord/index.html';
    });

    const params = new URLSearchParams(window.location.search);
    const noteId = params.get("noteId");
    fetchNoteList(noteId);
});

function fetchNoteList(noteId) {
    const dataToSend = {
        noteId: noteId
    };
    console.log(`noteId: ${noteId}`);
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/vocabulary/select/word', {
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
        drawWordList(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}

function drawWordList(list) {
    const contents = document.getElementById("contents");

    list.forEach(item => {
        const word = document.createElement('div');
        word.className = 'word';

        const original = document.createElement('div');
        original.className = 'original';
        original.textContent = item.word;

        const interpretation = document.createElement('div');
        interpretation.className = 'interpretation';
        interpretation.textContent = item.meaning;

        const examples = document.createElement('div');
        examples.className = 'example';

        item.examples.forEach(example => {
            const exampleOriginal = document.createElement('div')
            exampleOriginal.className = 'exampleOriginal';
            exampleOriginal.textContent = item.example;

            const exampleMeaning = document.createElement('div')
            exampleMeaning.textContent = item.meaning

            examples.appendChild(exampleOriginal);
            examples.appendChild(exampleMeaning);
        });

        const note1 = document.createElement('div');
        note1.textContent = item.note1;
        note1.className = 'note';

        const note2 = document.createElement('div');
        note2.textContent = item.note2;
        note2.className = 'note';

        const divider1 = document.createElement('div');
        divider1.className = 'divider';
        const divider2 = document.createElement('div');
        divider2.className = 'divider';
        const divider3 = document.createElement('div');
        divider3.className = 'divider';

        word.appendChild(original);
        word.appendChild(interpretation);
        word.appendChild(divider1);
        word.appendChild(examples);

        if (item.note1 && item.note1.trim() !== "") {
            word.appendChild(divider2);
            word.appendChild(note1);
        }
        if (item.note2 && item.note2.trim() !== "") {
            word.appendChild(divider3);
            word.appendChild(note2);
        }

        contents.appendChild(word);
    });
}