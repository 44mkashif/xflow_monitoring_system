var getTemps = $.get(window.location.pathname + '/temps');

getTemps.done(function(results) {
  var temperatures  = results.temperatures.slice(0,10);
  var timelist      = results.time.slice(0,10);
  // alert(timelist);
  var data = {
    // A labels array that can contain any sort of values
    labels: timelist.reverse(),
    // Our series array that contains series objects or in this case series data arrays
    series: [
      temperatures.reverse()
    ]
  };


  var options = {
    height: 300,
    high: Math.max.apply(Math,temperatures) + 5,
    low: Math.min.apply(Math,temperatures) - 5,
    onlyInteger: true,
  };

  // Create a new line chart object where as first parameter we pass in a selector
  // that is resolving to our chart container element. The Second parameter
  // is the actual data object.
  var myChart = new Chartist.Line('.ct-chart', data, options, {
    axisX : {
      type: Chartist.AutoScaleAxis,
    }
  });
});