// Plot demo graph 1

var dummyData1 = {[
    {'2012-07-3': 100},
    {'2012-07-3': 97},
    {'2012-07-3': 84},
    {'2012-07-3': 73},
    {'2012-07-3': 87},
    {'2012-07-3': 72},
    {'2012-07-3': 51},
    {'2012-07-3': 31},
    {'2012-07-3': 33}
    ]}

$(function () {
    var options = {
        xaxis: {
            mode: "time",
            timeformat: "%y/%m/%d",
        }
    };
    var d1 = [];
    for (var i = 0; i<dummyData1.length; i += 1){
        var d = new Date(2012, 07, 4+i);
        d1.push([d, Math.sin(i)]);
    }

    // a null signifies separate line segments
    // var d3 = [[0, 12], [7, 12], null, [7, 2.5], [12, 2.5]];




    $.plot($("#ua-sniff-chart"), [ d1 ], options);
});

// Plot demo graph 2
$(function () {
    var options = {
        xaxis: {
            mode: "time",
            timeformat: "%y/%m/%d",
        }
    };
    var d1 = [];
    for (var i = 0; i<14; i += 0.5){
        var d = new Date(2012, 07, 4+i);
        d1.push([d, Math.sin(i)]);
    }

    $.plot($("#prefixed-feature-chart"), [ d1 ], options);
});
