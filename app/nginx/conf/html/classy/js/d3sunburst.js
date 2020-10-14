var nodeData = JSON.parse(document.getElementById("nodeData").textContent);
var untranslate = JSON.parse(document.getElementById("untranslate").textContent);
var poptions = JSON.parse(document.getElementById("poptions").textContent);
var ex_options = JSON.parse(document.getElementById("ex_options").textContent);
var ex_poptions = JSON.parse(document.getElementById("ex_poptions").textContent);


var pieoptions = {
    //responsive: true,
    //maintainAspectRatio: true,
    //aspectRatio: 1,
    onClick: searchEvent,
    legend: {
        display: false
    },
    title: {
        display: false
    },
    layout: {
        padding: {
            //right: 50
            //left: 50
            //bottom: 100
        }
    },
    onResize: afterResizing
};


var config = {
    type: 'doughnut',
    data: nodeData,
    options: pieoptions
};

$(document).ready(function() {
    var ctx = document.getElementById("donutChart").getContext("2d");
    var mydog = new Chart(ctx, config);
});

function searchEvent(event, array) {
    if (array[0]) {
        if (ex_options.includes(poptions[array[0]._index])) {
            $("#advanced-form #id_classification").val(untranslate[poptions[array[0]._index]]);
            console.log('first');
        } else {
            $("#advanced-form #id_protected_type").val(untranslate[poptions[array[0]._index]]);
            console.log('second');
        }
        $("#searchi").submit();
        //$("#pieChartClassi").val(untranslate[options[array[0]._index]]);
        //$("#advanced-form  #id_classification").val(untranslate[poptions["UN"]]);
        //$("#advanced-form #id_classification").val(untranslate[poptions[array[0]._index]]);
        //console.log(untranslate);
        //console.log(poptions[array[0]._index]);
        //console.log(poptions[array[0]._index] in untranslate);
        //$("#advanced-form select#id_classification option[value='" + poptions[array[0]._index] + "']").prop("selected", true);
        //console.log($("#advanced-form select#id_classification").val());
        //console.log(poptions[array[0]._index]);
    }
};
//*[@id="id_classification"]
document.querySelector("#id_classification")

function afterResizing(chart, size) {
    if(size.width <= 200 | size.height > 150) {
        $("#pieChart").hide();
    } else {
        $("#pieChart").show();
    }
    chart.update();
};
