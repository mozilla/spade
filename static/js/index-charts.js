// Plot demo graph 1

var dummyData1 = {
    '2012-07-03': 100,
    '2012-07-04': 97,
    '2012-07-05': 84,
    '2012-07-06': 73,
    '2012-07-07': 87,
    '2012-07-08': 72,
    '2012-07-09': 51,
    '2012-07-10': 31,
    '2012-07-11': 33,
    };

$(function () {
    var options = {
        xaxis: {
            mode: "time",
            timeformat: "%y/%m/%d",
        }
    };
    var d1 = [];

    // Parse dummy data into graph
    for(date in dummyData1){
        var d = new Date(date);
        d1.push([d, dummyData1[date]]);
        console.log(d)
    }

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
