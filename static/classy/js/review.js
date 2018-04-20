
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
	denied.push(event.target.id);
	row.remove();
});

$body = $('body');

/*$(document).on({
	ajaxStart: function() {	$body.addClass('loading'); },
	ajaxStop: function() { $body.removeClass('loading'); }
});*/

$(document).on('click', '.subby', function() {
	$body.addClass('loading');

	var tmp = event.target.id;
	$.ajax({
		type: 'POST',
		url: 'review',
		traditional: true,
		data: {'denied': JSON.stringify(denied), 'csrfmiddlewaretoken': csrftoken, 'group': event.target.id},

		success: function(data){
			if(data.status == 1) {
				$('#succ').submit();
			} else {
				$('#fail').submit();
			}
		}
	});

});

$(document).on('click', '.deny', function() {
	$body.addClass('loading');
	var tmp = event.target.id;
	$.ajax({
		type: 'POST',
		url: 'review',
		traditional: true,
		data: {'csrfmiddlewaretoken': csrftoken, 'group': event.target.id},

		success: function(data) {
			if(data.status == 1) {
				$('#succ').submit();
			} else {
				$('#fail').submit();
			}
		}
	});
});
		

