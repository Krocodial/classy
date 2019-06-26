var classification_mapping = JSON.parse(document.getElementById("classification_mapping").textContent);

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
    data: classification_mapping,
    options: pieoptions
};

var ctx = document.getElementById("donutChart").getContext("2d");
var mydog = new Chart(ctx, config);


function searchEvent(event, array) {
    if (array[0]) {
        $("#pieChartClassi").val(untranslate[options[array[0]._index]]);
        console.log(array[0]._index);
    }
};
