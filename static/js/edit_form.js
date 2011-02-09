// $(function(){
function save_field_value(){
    var val = $(this).val();
    if (val=="-1"){ 
        return false;
    }   
    var arr = val.split('_');
    $.fancybox.showActivity();
    $.ajax({
        type        : "POST",
        cache   : false,
        url     : '/lead/moss/ufld',
        data    : 'field='+arr[0]+'&value='+arr[1],
        success: function(data) {
           if(data.code=='OK'){
        	   $.fancybox.hideActivity();
        	   if (data.clear_selection!=null){
            	   for (var j=0; j<data.clear_selection.length; j++){
                       $('#'+data.clear_selection[j]).empty().append('<option selected value="-1">Please select...</option>') ;
                       $('#icon_'+data.clear_selection[j]).hide();
                   }
        	   }
        	   if(data.next){
        		   var $select = $('#'+data.next);
        		   $.each(data.options, function(val, text) {
                       $select.append( new Option(text,val) );
                   });
        	   }
               $('#icon_'+arr[0]).html('<img src="/static/icons/package-install.png"/>');
               $('#icon_'+arr[0]).show();
               if (data.is_complete){
               }
           }else{
               $('#icon_'+arr[0]).css('width:100px').html('<strong>data.message</strong>');
               $('#icon_'+arr[0]).show();
           }
        },
    },'json'); 
    return false;
};

function save_input_field(){
    var field_id = $(this).attr('name');
    var value = $(this).attr('value');
    
    $.fancybox.showActivity();
    $.ajax({
        type    : "POST",
        cache   : false,
        data    : {'field_id':field_id, 'value':value},
        url     : '/lead/ucfld',
        success: function(data) {
           $.fancybox.hideActivity();
           if(data.code=='OK'){
               $('#icon_'+field_id).html('<img src="/static/icons/package-install.png"/>');
               $('#icon_'+field_id).show();
               if (data.is_complete){
            	   
               }
           }else{
               alert(data.code+':'+data.message);
           }
        }   
    },'json');
   
            return false;
        }
        
        function fold_group (){
            var $field_groups = $(this).next().next();
            $field_groups.slideToggle('slow');
    return false;
};

function delete_new_group(){
    alert('Delete of '+ $(this).attr('id'));
    return false;
};
function add_new_group(){
    var $field_groups = $(this).parent();
    var fg_visible = $field_groups.is(":visible");
    $.fancybox.showActivity();
    $.ajax({
         type        : "POST",
         cache   : false,
         url     : $(this).attr('href'),
         data    : {'refgrp':$(this).attr('id')},
         success: function(data) {
        	$.fancybox.hideActivity(); 
        	$('.field_value_select').unbind('change');
        	$('.common_field').unbind('change', save_input_field);
            $(".fold_group").unbind('click');
            $(".add_group").unbind('click');
            $(".delete_group").unbind('click');
            
        	$field_groups.append (data );
            
            $('.field_value_select').bind('change', save_field_value);
            $(".fold_group").bind('click', fold_group);
            $(".add_group").bind('click', add_new_group);
            $(".delete_group").bind('click', delete_new_group);
            $('.common_field').bind('change', save_input_field);
         }   
    });
    
    return false;
};
//    });        