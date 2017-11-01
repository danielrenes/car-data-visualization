const color_free = "#191";
const color_occupied = "#f02";
var heatmap_spots = [];

/**
 * Create one grid element.
 * @param {Integer} lat latitude of the top left corner for the grid element
 * @param {Integer} lon longitude of the top left corener for the grid element
 * @param {String} color color of the grid element
 */
var grid = function(lat, lon, color) {
  
};

/**
 * Draw a heatmap spot to the map.
 * @param {Integer} lat latitude of the drawing center
 * @param {Integer} lon longitude of the drawing center
 * @param {Integer} radius radius of the circle
 * @param {String} color color of the circle
 */
var heatmap = function(lat, lon, radius, color) {
  heatmap_spots.push(L.circle([lat, lon], {
    color: color,
    fillColor: color,
    fillOpacity: 0.5,
    radius: radius
  }).addTo(map));
};

var replay = function(data) {
  let index = 0;
  replay_interval_id = setInterval(function() {
    for (let i = 0; i < heatmap_spots.length; i++) {
      map.removeLayer(heatmap_spots[i]);
    }
    heatmap_spots.length = 0;
    for (let key in data) {
      let splitted = key.split(",");
      let lat = splitted[0];
      let lon = splitted[1];
      let color = data[key][index] == 0 ? color_free : color_occupied;
      console.log(lat + "," + lon + ": " + data[key][index] + " => " + color);
      heatmap(lat, lon, 10, color);
    }
    index++;
  }, 1000);
};
