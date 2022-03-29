// import moment from 'moment';

export function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export function getNextDueDate(start, interval) {
    let start_date = moment(start)
    switch (interval) {
        case 'daily':
            return start_date.add(1, 'd')
        case 'weekly':
            return start_date.add(1, 'w')
        case 'bi-weekly':
            return start_date.add(2, 'w')
        case 'semi-weekly':
            return start_date.add(4, 'd')
        case 'ten day':
            return start_date.add(10, 'd')
        case 'monthly':
            return start_date.add(1, 'M')
        case 'semi-monthly':
            // TODO: build a better semi-monthly algorithm
            return start_date.add(15, 'd')
        case 'quarterly':
            return start_date.add(1, 'Q')
        case 'annually':
            return start_date.add(1, 'y')
        case 'semi-annually':
            return start_date.add(6, 'M')
        case 'biennial':
            return start_date.add(2, 'y')
        case 'triennial':
            return start_date.add(3, 'y')
        default:
            throw new Error('Unknown Inspection Interval :: ' + interval)
    }
}