$(function(){
    $('.error').tooltip({
        position: 'center right',
        offset: [0, 5]
    });
    
    $('textarea').autoResize({
        extraSpace : 15
    });
    
    addtoggle();
});

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
