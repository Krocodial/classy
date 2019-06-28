var nodeData = JSON.parse(document.getElementById("nodeData").textContent);
var untranslate = JSON.parse(document.getElementById("untranslate").textContent);
var poptions = JSON.parse(document.getElementById("poptions").textContent);

var pieoptions = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1,
    onClick: searchEvent,
    legend: {
        display: false
    },
    title: {
        display: false
    },
};


var config = {
    type: 'doughnut',
    data: nodeData,
    options: pieoptions
};

var ctx = document.getElementById("donutChart").getContext("2d");
var mydog = new Chart(ctx, config);


function searchEvent(event, array) {
    if (array[0]) {
        //$("#pieChartClassi").val(untranslate[options[array[0]._index]]);
        $("#advanced-form > #id_classification").val(untranslate[poptions["UN"]]);
        console.log(poptions[array[0]._index]);
    }
};
