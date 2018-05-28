function selectOccupation(type){
  $('.occupation-input').hide();

  $('#'+type.value).show();

  if(type.value == "retired"){
    $('#federal').show();
  }
  if($.inArray(type.value, ['community', 'international', 'ngo', 'media', 'business', 'municipal']) != -1){
     $('#id_organization').parent().show();
  }

  if(type.value == 'none'){
    $('.occupation-input').hide();
  }
}

function selectSchool(school){
   $('.school').hide();
   val = school.value.replace(/ /g, '');
   $('#'+val).parent().show();
}

function selectMinistry(ministry){
   $('.ministry').hide();
   val = ministry.value.replace(/ /g, '').toLowerCase();
   $('#'+val+'-ministry').parent().show();
}

function validateEmail(form){
      if(form.value != ''){
        $.ajax({
            url: 'http://localhost:8000/validateemail',
            data: { 'email': form.value },
            dataType: 'json',
            success: function(data){
              if(data.valid == true){
                $('.valid-icon').html('<img src="'+check+'">');
                $('#email-valid-error').html('');
              } else {
                $('.valid-icon').html('<img src="'+ex+'">');
                $('#email-valid-error').html('<div style="margin-top:5px" class="ui negative message"><p>'+gettext("The email address used is not included in our list of pre-approved emails or domain.")+'</p><a href="https://gccollab.ca/terms">'+gettext("Who can register?")+'</a></div>');
              }
            }
        })
      } else {
        $('.valid-icon').html('');
        $('#valid-announcement').html('');
        $('#email-valid-error').html('');
      }
}
