function replaceprefix(formcontainer, newprefix){
    formcontainer.find('input, select, textarea')
        .attr('name', function(){
            return this.name.replace('%%%prefix%%%', newprefix);
        })
        .attr('id', function(){
            return this.id.replace('%%%prefix%%%', newprefix);
        });
}
