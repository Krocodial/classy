var nodeData = JSON.parse(document.getElementById("nodeData").textContent);
var untranslate = JSON.parse(document.getElementById("untranslate").textContent);
var poptions = JSON.parse(document.getElementById("poptions").textContent);

var pieoptions = {
    legend: {
        display: true,
        position: 'right'
    },
    title: {
        display: true
    },
    layout: {
        padding: {
            //right: 50
            //left: 50
            //bottom: 100
        }
    }
};


var pieconfig = {
    type: 'doughnut',
    data: nodeData,
    options: pieoptions
};

    var ctx = document.getElementById("donutChart").getContext("2d");
    var mydog = new Chart(ctx, pieconfig);

