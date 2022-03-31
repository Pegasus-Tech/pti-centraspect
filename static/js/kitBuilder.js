$('#new-component-form').on('submit', function (event) {
    event.preventDefault()

    let vals = {}
    for(let i = 0; i<event.target.length; i++) {
        let el = event.target[i]
        if(el.tagName.toLowerCase() === 'input') {
            console.log(el.value)
            vals[el.name] = el.value === '' ? '--' : el.value
            el.value = ''
        }
    }

    let tbody = $('#component-table-body')
    tbody.append('<tr>' +
        '<td>' + vals.component_name + '</td>' +
        '<td>' + vals.component_serial_number + '</td>' +
        '<td>' + vals.component_model_number + '</td>' +
        '<td>' + vals.component_expiration + '</td>' +
        '<td>' + vals.component_expiration + '</td>' +
        '</tr>')
    console.log("Component Vals :: ", vals)
    UIkit.modal($('#new-component-modal')).hide()
})