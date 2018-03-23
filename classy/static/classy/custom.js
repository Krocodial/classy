
//$('li').attr('unselectable', 'on'); //IE
var keys = [];
$(document).ready(function() {

	var ctr_pressed = false;
	var shift_pressed = false;	
	var last;
	var big;

	$(document).keydown(function(event) {
		ctr_pressed = event.keyCode==17;
		shift_pressed = event.keyCode==16;
	});

	$(document).keyup(function(event) {
		ctr_pressed = false;
		shift_pressed = false;
	});
	

	$('.data tbody').on('click', 'tr', function() {
		if(shift_pressed) {
			
			$.each(keys, function(index, value) {
                                $(value).toggleClass('selected');
                        });


			keys = [];
			if(this.id > last){
				big = this.id;
			} else {
				big = last;
				last = this.id;
			}
			for(i = last; i<=big; i++) {
				console.log($('#'+i));
				$('#'+i).toggleClass('selected');

				keys.push($('#' + i));
			}
			//alert(keys);
		} else if(ctr_pressed) {
			$(this).toggleClass('selected');
			keys.push($(this));
		} else {
			
			console.log('#'+this.id);

			//$('.row' + this.id).toggleClass('collapse');
			$.each(keys, function(index, value) {
				$(value).toggleClass('selected');
			});
			keys = [];
		}
		last = this.id;
	});
});
		
/*$(document).on('click', '#edito', function() {
	var rows = $.map(keys, function(value, index) {
	return '<tr><td>' + value.id + '</td><td>' + value.classy + '</td></tr>';
	});
	$('#batch tbody').html(rows.join(''));
});*/	

$(document).on('click', '#changeC', function() {
	//alert();
	/*$.each(keys, function(index, value) {
		console.log($(value).attr('id'));
	});*/
	var newy = $('#newC').find(':selected').text();
	$.each(keys, function(index, value) {
		chan = {id: $('#prodId' + $(value).attr('id')).attr('value'), classy: newy};
		toMod.push(chan);
	});

	//console.log($('#newC').find(':selected').text());
	$.each(keys, function(index, value) {
		$(value).toggleClass('selected');
	});
	keys = [];
});

//script to modify vals.
var toDel = [];
var toMod = [];

$('#contentArea').on('click', '.del', function() {
        var row = '.hiddenRows' + event.target.id;
        var mrow = '.mrow' + event.target.id;
        var rowId = '#prodId' + event.target.id;

        var id = $(rowId).attr('value');
        toDel.push(id);
        $(row).remove();
        $(mrow).remove();
});

$(document).on('change', '.cla', function(e) {
        var row = '.hiddenRows' + event.target.id;
        var rowId = '#prodId' + event.target.id;
        var newCl = this.options[e.target.selectedIndex].text;
        var fid = $(rowId).attr('value');

        chan = {id:fid, classy: newCl};
        toMod.push(chan);
});

$(document).on('click', '#subby', function() {
        var rows = $.map(toDel, function(value, index) {
        return '<tr><td>' + value + '</td><td>' +
                '<button class="btn btn-sm btn-danger float-right" type="button">Remove</button>' +
                '</td></tr>';
});

        $('#delTable tbody').html(rows.join(''));

        var rows = $.map(toMod, function(value, index) {
        return '<tr><td>' + value.id + '</td><td>' + value.classy + '</td><td>' +
                '<button class="btn btn-sm btn-danger float-right" type="button">Remove</button>' +
                '</td></tr>';
});

        $('#modTable tbody').html(rows.join(''));


});

$('#modTable').on('click', 'button', function() {
      var row = $(this).closest('tr');
      toMod.splice(row.index(), 1);
      row.remove();
});

$('#delTable').on('click', 'button', function() {
      var row = $(this).closest('tr');
      toDel.splice(row.index(), 1);
      row.remove();
});

/*
$(document).on('click', '#finSubby', function() {
        //alert(JSON.stringify(toDel));
        $.ajax({
                type: "POST",
                url: 'modi',
                traditional: true,
                data: {'toDel': JSON.stringify(toDel), 'toMod': JSON.stringify(toMod), 'csrfmiddlewaretoken': '{{ csrf_token }}'},

        success: function(data){
                if(data.status == 1) {
                $('#succ').submit();
                console.log('test');
        } else {
                $('#fai').submit();
                console.log('error');
                //window.location('url')
        }

        }
});
});
*/


