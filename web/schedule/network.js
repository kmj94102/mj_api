function getCurrentYear() {
    const currentDate = new Date();
    return currentDate.getFullYear();
  }
  
function getCurrentMonth() {
    const currentDate = new Date();
    return currentDate.getMonth() + 1;
}

function getSchedule(year = getCurrentYear(), month = getCurrentMonth()) {
    const url = `https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/calendar/select/month?year=${year}&month=${month}`

    return fetch(url)
    .then(response => {
        if(!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        drawCalendar(data, year, month);
        return data;
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation : ', error)
    });
}

function updateTaskStatus(id, isCompleted, date) {
    const dataToSend = {
        id: id,
        isCompleted: isCompleted,
        date: date
    };
    
    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/calendar/update/task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {  })
    .catch(error => {
        console.error('Error:', error);
        alert(`${error}`)
    });
}

function drawCalendar(data, year, month) {
    const calendarContainer = document.getElementById('calendar');
    calendarContainer.innerHTML = '';

    // 해당 월의 첫 날과 마지막 날 계산
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);

    // 해당 월의 일 수 계산
    const daysInMonth = lastDay.getDate();

    // 해당 월의 첫 날이 속한 주의 첫 날까지 이동
    for (let i = 0; i < firstDay.getDay(); i++) {
      const emptyDay = document.createElement('div');
      emptyDay.className = 'day';
      calendarContainer.appendChild(emptyDay);
    }

    // 각 날짜에 대한 처리
    for (let day = 1; day <= daysInMonth; day++) {
      const currentDate = new Date(year, month - 1, day);
      const dayContainer = document.createElement('div');
      dayContainer.className = 'day';

      const dayData = data.find(item => item.date === currentDate.toISOString().split('T')[0]);

      if (dayData) {
        dayContainer.innerHTML = `<strong>${day}</strong>`;

        dayData.scheduleInfoList.forEach(schedule => {
          const eventElement = createEventElement(schedule);
          dayContainer.appendChild(eventElement);
        });

        dayData.planInfoList.forEach(plan => {
          const planElement = createPlanElement(plan, `${year}.${month}.${day}`);
          dayContainer.appendChild(planElement);
        });
      } else {
        dayContainer.textContent = day;
      }

      calendarContainer.appendChild(dayContainer);
    }
  }

function createEventElement(schedule) {
    const eventElement = document.createElement('div');
    eventElement.className = 'event';
    eventElement.innerHTML = schedule.scheduleTitle;

    eventElement.onclick = () => openDialog(schedule.scheduleTitle, schedule.scheduleContent);

    return eventElement;
}

function createPlanElement(plan, date) {
    const planElement = document.createElement('div');
    planElement.className = 'plan';
    planElement.innerHTML = plan.title;

    planElement.onclick = () => openPlanDialog(plan.title, plan.taskList, date);

    return planElement;
}

function openDialog(title, content) {
    const dialogTitleElement = document.getElementById('dialogTitle');
    const dialogContentElement = document.getElementById('dialogContent');

    dialogTitleElement.textContent = title;
    dialogContentElement.innerHTML = content;

    document.getElementById('dialog').style.display = 'block';
    document.getElementById('dimLayer').style.display = 'block';
}

function openPlanDialog(title, contents, date) {
    const dialogTitleElement = document.getElementById('dialogTitle');
    const dialogContentElement = document.getElementById('dialogContent');
    dialogContentElement.innerHTML = '';

    dialogTitleElement.textContent = title;

    contents.forEach(task => {
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = task.isCompleted === true;

      const taskContent = document.createElement('span');
      taskContent.innerHTML = task.contents;
      taskContent.style.textDecoration = checkbox.checked ? 'line-through' : 'none';

      checkbox.addEventListener('change', () => {
        taskContent.style.textDecoration = checkbox.checked ? 'line-through' : 'none';
        updateTaskStatus(task.id, checkbox.checked, date)
      });

      const container = document.createElement('div');
      container.appendChild(checkbox);
      container.appendChild(taskContent);
      dialogContentElement.appendChild(container);
    });

    document.getElementById('dialog').style.display = 'block';
    document.getElementById('dimLayer').style.display = 'block';
  }

  function closeDialog() {
    document.getElementById('dialog').style.display = 'none';
    document.getElementById('dimLayer').style.display = 'none';
  
    const dialogContentElement = document.getElementById('dialogContent');
    dialogContentElement.innerHTML = '';
  }

function getDate(year = getCurrentYear(), month = getCurrentMonth()) {
    const formattedMonth = String(month).padStart(2, '0');
    document.getElementById('date').innerHTML = `${year}.${formattedMonth}`;
}
  
function openDateDialog() {
    document.getElementById('dialogContainer').style.display = 'block';
    document.getElementById('dimLayer').style.display = 'block';

    const currentDate = new Date();
    document.getElementById('year').value = currentDate.getFullYear();
    document.getElementById('month').value = currentDate.getMonth() + 1;
  }

function applyDate() {
    const year = document.getElementById('year').value;
    const month = document.getElementById('month').value;

    closeDateDialog();

    getDate(year, month);
    getSchedule(year, month);
}

function closeDateDialog() {
    document.getElementById('dialogContainer').style.display = 'none';
    document.getElementById('dimLayer').style.display = 'none';
}

getDate();
getSchedule();

document.getElementById('date').addEventListener('click', () => {
    openDateDialog();
});
