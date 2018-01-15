var traces = [];
for (i = 0; i < graphData.length; i++) {
    var converted_x = [];
    for (j = 0; j < graphData[i]['x'].length; j++) {
        converted_x.push(new Date(graphData[i]['x'][j]));
    }
    traces.push({x: converted_x,
                 y: graphData[i]['y'],
                 mode: 'lines',
                 text: graphData[i]['text'],
                 textposition: 'bottom',
                 type: 'scatter',
                 name: graphData[i]['course_name']});
}
var layout = {
    showlegend: true,
    legend: {
        "orientation": "h",
        x: 0,
        y: 100
    },
    xaxis: {
      tickformat: '%-m/%-d',
      title: 'Time'
    },
    yaxis: {
      hoverformat: '.2f',
      title: 'Grade [%]'
    }
};
Plotly.newPlot('graph', traces, layout);
var graph = document.getElementById('graph');
window.onresize = function() {
    Plotly.Plots.resize(graph);
};
$('#fs-button').click(function(){
    $('#fs-panel').toggleClass('fullscreen');
    Plotly.Plots.resize(graph);
});
$(document).ready(function() {
    Plotly.Plots.resize(graph);
});