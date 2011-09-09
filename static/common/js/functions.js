$(function(){
    $('.error').tooltip({
        position: 'center right',
        offset: [0, 5]
    });
    
    //$('textarea').autoResize({
    //    extraSpace : 15
    //});
    
    addtoggle();
    
    makecleditor();
});

function makecleditor(){
    $('textarea.rich').cleditor({
        bodyStyle: 'background-color:#D7FFCE; font:10pt Arial,Verdana;',
        width: '',
        height: 150,
        controls: "bold italic underline strikethrough subscript superscript | font size | color highlight removeformat | bullets numbering | outdent indent | alignleft center alignright | undo redo | link unlink | cut copy paste pastetext"
    });
}

function addtoggle(){
    $('legend .toggle').remove();
    $('legend').prepend("<div class='toggle'></div>");
    $('legend .toggle').click(function(){
        $(this).parent().parent().toggleClass('collapsed');
    });
}

function replaceprefix(formcontainer, newprefix){
    formcontainer.find('input, select, textarea, div, span')
        .attr('name', function(){
            if(this.name){
                return this.name.replace('%%%prefix%%%', newprefix);
            }
        })
        .attr('id', function(){
            if(this.id){
                return this.id.replace('%%%prefix%%%', newprefix);
            }
        });
}

function deleteitem(prefix){
    $('#id_' + prefix + '-delete').val('1');
    $('.' + prefix).hide();
}

function updatelabel(prefix, fieldname, value){
    if(value === ''){
        value = '[unnamed]';
    }
    $('#' + prefix + fieldname + 'label').html(value);
}
