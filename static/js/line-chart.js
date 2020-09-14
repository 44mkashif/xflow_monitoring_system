var data = {
  // A labels array that can contain any sort of values
  labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  // Our series array that contains series objects or in this case series data arrays
  series: [
    [48, 49, 48.5, 50, 47.9, 48.3, 48.9, 50.2, 49.7, 49.3, 49]
  ]
};

var options = {
  height: 300
};

// Create a new line chart object where as first parameter we pass in a selector
// that is resolving to our chart container element. The Second parameter
// is the actual data object.
var myChart = new Chartist.Line('.ct-chart', data, options);