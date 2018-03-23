
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');


denied = [];

$(document).on('click', '.remo', function() {
	var row = $(this).closest('tr');
	//console.log(row.index());	
	console.log(event.target.id);
	denied.push(event.target.id);
	row.remove();
});

$(document).on('click', '.subby', function() {


	var tmp = event.target.id;
	$.ajax({
		type: 'POST',
		url: 'review',
		traditional: true,
		data: {'denied': JSON.stringify(denied), 'csrfmiddlewaretoken': csrftoken, 'group': event.target.id},

		success: function(data){
			if(data.status == 1) {
				console.log(tmp);
				$('#succ').submit();
				//location.reload(true);
				
			} else {
				$('#faig').submit();
				console.log('failure');
				//location.reload(true);
			}
		}
	});

});
