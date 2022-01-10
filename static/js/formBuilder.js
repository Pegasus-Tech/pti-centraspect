import { getCookie } from './utils.js'

// setup the form builder options
const builderOptions = {
    controlPosition: 'right',
    controlOrder: ['header', 'paragraph', 'text', 'textarea', 'date', 'select', 'checkbox-group', 'radio-group', 'file'],
    disabledActionButtons: ['data', 'save', 'clear'],
    disableFields: ['autocomplete', 'hidden', 'starRating', 'button'],
    disabledAttrs: ['className', 'toggle', 'access', 'name'],
      onAddField: function(fieldId, fieldData) {
        fieldData = processFormAttributes(fieldData)
      }
}

// build the form builder object to render
const formBuilder = $('#fb-editor').formBuilder(builderOptions);
const logFormFB = $('#fb-log-form').formBuilder(builderOptions);


// handle form clear/save button actions
jQuery(function($) {
    $('#clear-form').on('click', function() {
        formBuilder.actions.clearFields();
    });

    $('#save-form').on('click', function() {
        const form = $('#new-inspection-form-form')[0]
        const requestUrl = form.action
        const method = form.method

        let json = formBuilder.actions.getData('json')
        let title = $('#form-title-input').val()
        let form_data = {form_json: json, title: title}
        let csrfToken = getCookie('csrftoken');
        console.log('token', csrfToken)
        if(csrfToken) {
            $.ajax({
                url: requestUrl,
                method: method,
                headers: {
                    'X-CSRFToken': csrfToken
                },
                data: form_data
            }).success(response => {
                console.log(response);
                window.location.href = response.url
            }).error(e => {
                console.error(e);
            })
        } else {
            alert('No Sercurity Token Available. Please logout and login again to retore your session security cookies.')
        }
    })
});


// render the form on loading
jQuery(function($) {
    let fbTemplate = document.getElementById('fb-template');
    if(fbTemplate){
        $('.fb-render').formRender({
            dataType: 'json',
            formData: fbTemplate.textContent
          });
    }
});

jQuery(function($) {
    let fbTemplate = document.getElementById('fb-log-form');
    if(fbTemplate){
        $('.fb-render').formRender({
            dataType: 'json',
            formData: fbTemplate.textContent
          });
    }
});

// save the form when a new form is logged
jQuery(function($) {

    $('#log-form-submit').on('click', function() {
        const form = $('#log-new-inspection-form')[0]
        const requestUrl = form.action
        const method = form.method
        
        let json = JSON.stringify($('.fb-render').formRender("userData"))
        let disposition = $('#form-disposition').val()
        let csrfToken = getCookie('csrftoken');

        let form_data = {middleware_token: csrfToken, form_json: json, disposition: disposition}
        if(csrfToken) {
            $.ajax({
                url: requestUrl,
                method: method,
                headers: {
                    'X-CSRFToken': csrfToken
                },
                data: form_data
            }).success(response => {
                window.location.href = response.url
            }).error(e => {
                console.error(e);
            })
        } else {
            alert('No Sercurity Token Available. Please logout and login again to retore your session security cookies.')
        }
    })
});



// adds custom classes to different field types when added to stage
function processFormAttributes(formData) {
    console.log(formData);
    switch (formData.type) {
        case 'text':
        case 'date':
        case 'file':
        case 'number':
            formData.className = 'uk-input'
            break;
        case 'textarea':   
            formData.className = 'uk-textarea'
            break;
        case 'select':
            formData.className = 'uk-select'
            break;
        case 'radio-group':
            formData.className = 'uk-radio'
            break;
        case 'checkbox-group':
            formData.className = 'uk-checkbox'
            break;

    }
    return formData
}
