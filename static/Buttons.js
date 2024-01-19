function addRow() {
    var table = document.getElementById("scheduleTable");
    var row = table.insertRow(-1);
    for (var i = 0; i < 3; i++) {
        var cell = row.insertCell(i);
        var textbox = document.createElement("input");
        textbox.type = "text";
        cell.appendChild(textbox);
    }
}

function removeRow() {
    var table = document.getElementById("scheduleTable");
    if (table.rows.length > 1) { // Prevents removing the header
        table.deleteRow(-1);
    }
}

function findUlBySpanText(dayText) {
    var spans = document.querySelectorAll('span');
    
    for (var i = 0; i < spans.length; i++) {
      if (spans[i].textContent.trim() === dayText) {
        var ul = spans[i].parentNode.nextElementSibling;

        if (ul && ul.tagName === 'UL') {
          return ul;
        }
       }
    }
    
    return null;
}
  
function fetchCoursesByID(courseId) {
    return fetch(`/get-courses-by-id?id=${courseId}`)
        .then(response => response.json())
        .then(data => {
            if (data) {
                return data[0];  
            } else {
                console.log('No data found');
                return null;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            return null;
        });
}

function extractDaysAndTimes(inputString) {
    const dayPattern = /(Mo|Tu|We|Th|Fr)/g;
    const timePattern = /\d{1,2}:\d{2}[ap]m/g;

    const days = inputString.match(dayPattern);
    const times = inputString.match(timePattern);

    const timeParts = times ? times.map(time => time.slice(0, -2)) : [];

    return [days, timeParts];
}

function createEvent(name, day, time) {
    switch(day) {
        case "Mo":
          day = "Monday"
          break;
        case "Tu":
          day = "Tuesday"
          break;
        case "We":
          day = "Wednesday"
          break;
        case "Th":
          day = "Thursday"
          break;
        case "Fr":
          day = "Friday"
          break;
    }

    var newEvent = document.createElement('li');
    newEvent.className = 'cd-schedule__event';

    newEvent.innerHTML = `
      <a data-start="${time[0]}" data-end="${time[1]}" data-content="${name}" data-event="event-7" href="#0">
        <em class="cd-schedule__name">${name}</em>
      </a>
    `;
    
    var scheduleDay = findUlBySpanText(day)
    if (scheduleDay)
    {
        scheduleDay.appendChild(newEvent);
    }
}

async function addNewEvent() {
    var inputElement = document.getElementById("input");
    var inputValue = inputElement.value;

    const course = await fetchCoursesByID(inputValue);
    if (!course)
    {
        return null
    }
    
    const name = course[0];
    const code = course[1];
    const time = course[2];
    const [days, times] = extractDaysAndTimes(time);

    for (var i = 0; i < days.length; i++) {
        createEvent(name, days[i], times)
    }
  }