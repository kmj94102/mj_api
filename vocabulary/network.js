document.addEventListener("DOMContentLoaded", function() {
    const submit = document.getElementById("submitGroup");
    const toast = document.getElementById("toast");

    const day = document.getElementById("day");
    const group = document.getElementById("group");
    const modify = document.getElementById("modify");
    const groupMeaning = document.getElementById("groupMeaning");

    submit.addEventListener("click", function(event){
        // 토스트 메시지 표시
        toast.textContent = day.value + "ㅎㅎ";
        toast.style.visibility = "visible";

        // 토스트 메시지 2초 후에 숨기기
        setTimeout(function() {
            toast.style.visibility = "hidden";
        }, 2000);

        fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app', {
                 method: 'POST',
                 headers: {
                     'Content-Type': 'application/json'
                 },
                 body: JSON.stringify({
                     day,
                     group,
                     word,
                     meaning,
                     hint,
                     additional
                 })
             })
             .then(response => response.json())
             .then(data => {
                 // Handle the response from the server
                 console.log(data);
                 // Clear input fields
                 document.getElementById("day").value = '';
                 document.getElementById("word").value = '';
                 document.getElementById("meaning").value = '';
                 document.getElementById("hint").value = '';
                 document.getElementById("additional").value = '';
             })
             .catch(error => {
                 console.error('Error:', error);
             });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const submit = document.getElementById("submitWord");
    const toast = document.getElementById("toast");

    const day = document.getElementById("day");
    const group = document.getElementById("group");
    const word = document.getElementById("word");
    const wordMeaning = document.getElementById("wordMeaning");
    const hint = document.getElementById("hint");
    const additional = document.getElementById("additional");

    submit.addEventListener("click", function(event){
        // 토스트 메시지 표시
        toast.textContent = day.value;
        toast.style.visibility = "visible";

        // 토스트 메시지 2초 후에 숨기기
        setTimeout(function() {
            toast.style.visibility = "hidden";
        }, 2000);

        word.value = ""
        wordMeaning.value = ""
        hint.value = ""
        additional.value = ""
    });
});