import { getCookie } from './utils.js'

export function editForm(formData) {
    // setup the form builder options

    console.log(formData);

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
    const editFb = $('#fb-editor-edit').formBuilder(builderOptions);

    console.log('formBuilder', editFb);
    editFb.promise.then(builder => {
        builder.actions.setData(formData)
    });

    $('#clear-edit-form').on('click', function() {
        editFb.actions.clearFields()
    });

    $('#save-edit-form').on('click', function() {
        const form = $('#edit-inspection-form-form')
        let json = editFb.actions.getData('json')
        $('#edit-form-json').val(json)
        form.submit()
    });
    
}

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