
export function loadFullCalendar(data) {
    document.addEventListener('DOMContentLoaded', function() {
      var calendarEl = document.getElementById('inspection-calendar');

      let options = {
        buttonText: {
          month: 'Month',
          week: 'Week',
          list: 'List',
          today: 'Today'
        },
        initialView: 'dayGridMonth',
        headerToolbar:{
          start: 'prev,next today',
          center: 'title',
          end: 'dayGridMonth,list'
        },
        themeSystem: 'bootstrap',
        events: data
      }

      var calendar = new FullCalendar.Calendar(calendarEl, options);
      calendar.render();
    });
}


