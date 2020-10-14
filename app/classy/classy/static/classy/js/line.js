var dates = JSON.parse(document.getElementById("dates").textContent);
var keys = JSON.parse(document.getElementById("keys").textContent);
var lineDataset = JSON.parse(document.getElementById("lineDataset").textContent);

var config = {
        type: 'line',
        data: {
                labels: dates,
                datasets: lineDataset

                      /*[{
                        label: 'Unclassified',
                        backgroundColor: '#bca9b6',
                        borderColor: '#94778B',
                        pointBackgroundColor: '#94778B',
                        pointBorderColor: '#fff',
                        pointHoverBorderColor: '#94778B',
                        data: keys['UN'],
                        fill: 'origin',
                        }, {
                        label: 'Public',
                        backgroundColor: '#adefa9',
                        borderColor: '#7CE577',
                        pointBackgroundColor: '#7CE577',
                        pointBorderColor: '#fff',
                        pointHoverBorderColor: '#7CE577',
                        data: keys['PU'],
                        fill: '-1',
                        }, {
                        label: 'Confidential',
                        backgroundColor: '#c8e2ea',
                        borderColor: '#A0CCDA',
                        data: keys['CO'],
                        fill: '-1',
                        }
                        ]*/
                },
                options: {
                        elements: {
                        },
                        legend: {
                                display: true,
                                position: 'bottom',
                        },
                        layout: {
                            padding: {
                                right: '10'
                            }
                        },
                        //responsive: true,
                        //maintainAspectRatio: true,
                        aspectRatio: '5',
                        onResize: lineResizing,
                        title: {
                                display: true,
                                text: 'Your data over the last 2 months',
                                position: 'top',
                                fontSize: '12'
                        },
                        tooltips: {
                                mode: 'index',
                                intersect: false,
                        },
                        hover: {
                                //mode: 'nearest',
                                //intersect: true
                        },
                        scales: {
                                xAxes: [{
                                        display: false,
                                        scaleLabel: {
                                                display: true,
                                                labelString: 'Date'
                                        }
                                }],
                                yAxes: [{
                                        stacked: true,
                                        display: true,
                                        scaleLabel: {
                                                display: true,
                                                labelString: 'Rows'
                                        }
                                }]
                        }
                }
        };


var line = document.getElementById('lineChart').getContext('2d');

window.onload = function() {
    window.myLine = new Chart(line, config);
    var size = {width: window.myLine.width};
    lineResizing(window.myLine, size);
};
function lineResizing(chart, size){
    if(size.width <=1000) {
        $("#lineChart").hide();
    } else {
        $("#lineChart").show();
        //chart.options.legend.display=true;
    }
    chart.update()
};

function afterResizing(chart, size){
    if(size.width <=530) {
        chart.options.legend.display=false;
    } else {
        chart.options.legend.display=true;
    }
    chart.update()
};
