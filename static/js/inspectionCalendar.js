
export function loadFullCalendar(inspection_data) {
    let data = []
    if(inspection_data) {
        for(let i = 0; i<inspection_data.length; i++) {
            let color = getEventColor(inspection_data[i])
            data.push(
                {
                    id: inspection_data[i].fields.uuid,
                    title: inspection_data[i].fields.title,
                    start: inspection_data[i].fields.next_inspection_date,
                    backgroundColor: color,
                    borderColor: color,
                    url: '/dashboard/inspection-items/'+inspection_data[i].fields.uuid
                }
            )
        }
    }

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
          // start: 'prev,next today',
          // center: 'title',
          // end: 'dayGridMonth,list'
            start: 'prev,next',
            center: 'title',
            end: 'today'
        },
        themeSystem: 'bootstrap',
        events: data
      }

      var calendar = new FullCalendar.Calendar(calendarEl, options);
      calendar.render();
    });


    function getEventColor(item) {
      switch(item.fields.inspection_type) {
        case 'facility':
          return '#fe6847'
        case 'ppe':
          return '#009688'
        case 'equipment':
          return '#fec601'
        case 'rescue':
          return '#1e87f0'
        case 'first aid':
          return '#C5283D'
        case 'vehicle':
          return '#5D5179'
        default:
          return '#dfe0e2'
      }
    }
}


