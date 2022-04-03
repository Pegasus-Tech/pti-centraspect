let tableIdx = 0;

$('#new-component-form').on('submit', function (event) {
    event.preventDefault()

    let vals = {}
    for(let i = 0; i<event.target.length; i++) {
        let el = event.target[i]
        if(el.tagName.toLowerCase() === 'input') {
            vals[el.name] = el.value === '' ? '--' : el.value
            el.value = ''
        }
    }

    let tbody = $('#component-table-body')
    let rowId = `subitem-row-${tableIdx}`
    tbody.append('<tr id=' + "\"" + rowId + "\"" + '>' +
        '<td>' + vals.component_name + '</td>' +
        '<td>' + vals.component_serial_number + '</td>' +
        '<td>' + vals.component_model_number + '</td>' +
        '<td>' + vals.component_expiration + '</td>' +
        '<td><a href="#" class="uk-button uk-button-link subitem-remove-btn">Remove</a></td>' +
        '</tr>')
    UIkit.modal($('#new-component-modal')).hide()
    tableIdx++
})

$("#sub-item-table").on("click", ".subitem-remove-btn", function(event) {
    event.preventDefault();
   $(this).closest("tr").remove();
});

$("#new-kit-form").on('submit', function(event) {
    event.preventDefault();
    let formData = {}
    let subItems = []
    let inputs = $('#new-kit-form :input');
    inputs.each(function() {
        if(this.tagName !== 'button' && this.tagName !== 'a' && this.tagName !== 'form') {
            formData[this.name] = $(this).val();
        }
    });

    let tableRows = $("#sub-item-table > tbody > tr");
    tableRows.each(function() {
        let rowId = this.id;
        let rowTds = $(`#${rowId} td`)

        let subItem = {
            "name": rowTds[0].innerText === '--' ? '' : rowTds[0].innerText,
            "serial_number": rowTds[1].innerText === '--' ? '' : rowTds[1].innerText,
            "model_number": rowTds[2].innerText === '--' ? '' : rowTds[2].innerText,
            "expiration_date": rowTds[3].innerText === '--' ? '' : rowTds[3].innerText
        }

        subItems.push(subItem);
    });

    formData['subItems'] = subItems;

    $.ajax({
        headers: {
          'X-CSRFToken': formData['csrfmiddlewaretoken']
        },
        method: 'POST',
        url: '/dashboard/inspection-items/kit',
        data: JSON.stringify(formData),
        success: resp => {
            window.location = '/dashboard/inspection-items/' + resp.item_uuid;
        },
        error: err => {
            console.error(err)
        }
    });
})
