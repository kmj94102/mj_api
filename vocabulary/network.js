document.addEventListener("DOMContentLoaded", function() {
    const submit = document.getElementById("submitGroup");
    const toast = document.getElementById("toast");

    const day = document.getElementById("day");
    const group = document.getElementById("group");
    const modify = document.getElementById("modify");
    const groupMeaning = document.getElementById("groupMeaning");

    submit.addEventListener("click", function(event){
        const data = {
            day: day.value,
            name: group.value,
            meaning: groupMeaning.value,
            modify: modify.value
        }
        fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/vocabulary/group/insert', {
                 method: 'POST',
                 headers: {
                     'Content-Type': 'application/json'
                 },
                 body: JSON.stringify(data)
             })
             .then(response => response.json())
             .then(data => {
                console.log(data);
                // 토스트 메시지 표시
                toast.textContent = data;
                toast.style.visibility = "visible";

                // 토스트 메시지 2초 후에 숨기기
                setTimeout(function() {
                    toast.style.visibility = "hidden";
                }, 2000);
             })
             .catch(error => {
                console.error('Error:', error);
                // 토스트 메시지 표시
                toast.textContent = "등록 실패";
                toast.style.visibility = "visible";

                // 토스트 메시지 2초 후에 숨기기
                setTimeout(function() {
                    toast.style.visibility = "hidden";
                }, 2000);
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
        const data = {
            day: day.value,
            group: group.value,
            word: word.value,
            meaning: wordMeaning.value,
            hint: hint.value,
            additional: additional.value
        }

        fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/vocabulary/insert', {
                 method: 'POST',
                 headers: {
                     'Content-Type': 'application/json'
                 },
                 body: JSON.stringify(data)
             })
             .then(response => response.json())
             .then(data => {
                console.log(data);
                // 토스트 메시지 표시
                toast.textContent = data;
                toast.style.visibility = "visible";

                // 토스트 메시지 2초 후에 숨기기
                setTimeout(function() {
                    toast.style.visibility = "hidden";
                }, 2000);
             })
             .catch(error => {
                console.error('Error:', error);
                // 토스트 메시지 표시
                toast.textContent = "등록 실패";
                toast.style.visibility = "visible";

                // 토스트 메시지 2초 후에 숨기기
                setTimeout(function() {
                    toast.style.visibility = "hidden";
                }, 2000);
             });

        word.value = ""
        wordMeaning.value = ""
        hint.value = ""
        additional.value = ""
    });
});