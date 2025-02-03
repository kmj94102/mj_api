document.addEventListener("DOMContentLoaded", function() {
    const newVocabulary = document.getElementById("newVocabulary");

    newVocabulary.addEventListener("click", function(event){
        window.location.href = 'addNote/index.html';
    });
});