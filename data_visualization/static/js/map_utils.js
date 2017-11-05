const color_free = "#191";
const color_occupied = "#f02";
var heatmap_spots = [];

/**
 * Draw a heatmap spot to the map.
 * @param {Integer} lat latitude of the drawing center
 * @param {Integer} lon longitude of the drawing center
 * @param {Integer} radius radius of the circle
 * @param {String} color color of the circle
 */
var heatmap_spot = function(lat, lon, radius, color) {
  heatmap_spots.push(L.circle([lat, lon], {
    color: color,
    fillColor: color,
    fillOpacity: 0.5,
    radius: radius
  }).addTo(map));
};

/**
 * Draw a heatmap.
 * @param {Integer} lat latitude of the drawing center
 * @param {Integer} lon longitude of the drawing center
 * @param {Integer} radiuses radiuses of the circles
 * @param {String} colores colors of the circles
 */
var heatmap = function(lat, lon, radiuses, colors) {
  for (let i = 0; i < radiuses.length; i++) {
    heatmap_spot(lat, lon, radiuses[i], colors[i]);
  }
}

var replay = function(data) {
  let index = 0;
  replay_interval_id = setInterval(function() {
    let clusters = create_clusters(data, 100);
    for (let i = 0; i < clusters.length; i++) {
      let cluster = clusters[i];
      let lat_center = 0;
      let lon_center = 0;
      let divider = 0;
      for (let j = 0; j < cluster.length; j++) {
        let item = cluster[j];
        let splitted = item[0].split(",");
        let lat = parseFloat(splitted[0]);
        let lon = parseFloat(splitted[1]);
        lat_center += lat;
        lon_center += lon;
        divider += 1;
      }
      lat_center /= divider;
      lon_center /= divider;
      let radiuses = [];
      let colors = [];
      let order = [];
      let item_index = 0;
      for (let j = 0; j < cluster.length; j++) {
        let item = cluster[j];
        let splitted = item[0].split(",");
        let lat = parseFloat(splitted[0]);
        let lon = parseFloat(splitted[1]);
        radiuses.push(distance_between(lat_center, lon_center, lat, lon));
        colors.push(item[1][index] == 0 ? color_free : color_occupied);
        order.push(item_index);
        item_index += 1;
      }
      order.sort(function(a, b) {
        return radiuses[a] < radiuses[b] ? 1 : radiuses[a] > radiuses[b] ? -1 : 0;
      });
      radiuses = order_by_index_array(radiuses, order);
      colors = order_by_index_array(colors, order);
      heatmap(lat_center, lon_center, radiuses, colors);
    }
    index++;
  }, 1000);
};

/**
 * Calculate distance between two geographical location.
 * @param {float} lat1 latitude of the first geolocation
 * @param {float} lon1 longitude of the first geolocation
 * @param {float} lat2 latitude of the second geolocation
 * @param {float} lon2 longitude of the second geolocation
 * @return {float} distance between the two geolocations in meters
 */
var distance_between = function (lat1, lon1, lat2, lon2) {
    var earth_radius = 6378.137;
    var diff_lat = lat2 * Math.PI / 180 - lat1 * Math.PI / 180;
    var diff_lon = lon2 * Math.PI / 180 - lon1 * Math.PI / 180;
    var a = Math.sin(diff_lat/2) * Math.sin(diff_lat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(diff_lon/2) * Math.sin(diff_lon/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    var d = earth_radius * c;
    return d * 1000;
}

/**
 * Order the given array based on the order of the indexes.
 * @param {Array} array the array to be sorted
 * @param {Array} order the ordered indexes
 * @return {Array} the ordered array
 */
var order_by_index_array = function(array, order) {
  let ordered = [];
  for (let i = 0; i < order.length; i++) {
    ordered.push(array[order[i]]);
  }
  return ordered;
}

var create_clusters = function(data, distance) {
  let clusters = [];
  let cluster_centers = [];
  for (let key in data) {
    let splitted = key.split(",");
    let lat = parseFloat(splitted[0]);
    let lon = parseFloat(splitted[1]);
    let i;
    for (i = 0; i < clusters.length; i++) {
      let cluster_center = cluster_centers[i];
      let n_points = clusters[i].length;
      if (distance_between(lat, lon, cluster_center[0] / n_points, cluster_center[1] / n_points) < distance) {
        clusters[i].push([key, data[key]]);
        cluster_centers[i][0] += lat;
        cluster_centers[i][1] += lon;
        break;
      }
    }
    if (i == clusters.length) {
      let cluster = [];
      cluster.push([key, data[key]]);
      let center = [lat, lon];
      clusters.push(cluster);
      cluster_centers.push(center);
    }
  }
  return clusters;
}
