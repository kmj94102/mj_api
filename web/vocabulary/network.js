let year = 2025;
let month = 1;

document.addEventListener("DOMContentLoaded", function() {
    const today = new Date();
    year = today.getFullYear();
    month = today.getMonth() + 1;

    const newVocabulary = document.getElementById("newVocabulary");
    document.getElementById("date").textContent = `${year}.${month.toString().padStart(2, '0')}`;
    fetchNotes();

    newVocabulary.addEventListener("click", function(event){
        window.location.href = 'addNote/index.html';
    });
});

async function fetchNotes() {
    const dataToSend = {
        year: year,
        month: month
    };
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/vocabulary/select/note', {
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
        drawNoteList(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}

function drawNoteList(list) {
    const noteList = document.getElementById("noteList");

    list.forEach(item => {
        console.log('draw', item.title);
        const note = document.createElement('div');
        note.className = 'note';
        note.setAttribute('data-text', item.noteId);

        const noteContents = document.createElement('div');

        const noteTitle = document.createElement('span');
        noteTitle.className = 'noteTitle';
        const date = new Date(item.timestamp);
        const formattedDate =
            `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
        noteTitle.textContent = formattedDate;

        const noteSubContents = document.createElement('div');
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = item.language == 'us' ? '영어' : '일본어';

        const noteName = document.createElement('span');
        noteName.className = 'noteName';
        noteName.textContent = item.title;

        noteSubContents.appendChild(tag);
        noteSubContents.appendChild(noteName);

        noteContents.appendChild(noteTitle);
        noteContents.appendChild(noteSubContents);

        const image = document.createElement('img');
        image.src = "ic_next.svg";

        note.appendChild(noteContents);
        note.appendChild(image);

        note.addEventListener("click", function(event){
            const value = item.noteId;
            window.location.href = `note/index.html?noteId=${encodeURIComponent(value)}`;
        });

        noteList.appendChild(note);
    });
}