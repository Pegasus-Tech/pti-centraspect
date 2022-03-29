// import moment from 'moment';
import {getNextDueDate} from "./utils.js";

export function loadFullCalendar(inspection_data) {
    let data = []
    console.log(inspection_data)
    if(inspection_data) {
        for(let i = 0; i<inspection_data.length; i++) {
            let color = getEventColor(inspection_data[i])
            data.push(
                {
                    id: inspection_data[i].uuid,
                    title: getEventTitle(inspection_data[i]),
                    start: inspection_data[i].due_date,
                    backgroundColor: color,
                    borderColor: color,
                    url: '/dashboard/inspection-items/'+inspection_data[i].item_uuid,
                    display: 'list-item'
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

    function getEventTitle(inspection) {
        if(inspection.missed) {
            return inspection.title + " - MISSED"
        } else if (inspection.completed_past_due) {
            return inspection.title + " - CPD"
        } else if (inspection.completed_date !== null && inspection.completed_date != "None") {
            return inspection.title + " - DONE"
        } else {
            return inspection.title
        }
    }

    function getCalendarVisibilityRange() {
        let today = moment()
        let two_years = today.add(2, 'y').format('yyyy-MM-DD')
        console.log("Two Years Out ", two_years)
        return two_years
    }

    function getEventColor(inspection) {
      switch(inspection.inspection_type) {
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


