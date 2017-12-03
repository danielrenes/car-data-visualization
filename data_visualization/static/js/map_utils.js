var heat = null;

var replay = function(data) {
  let index = 0;
  replay_interval_id = setInterval(function() {
    if (heat !== null) {
      console.log("remove layer");
      map.removeLayer(heat);
    }
    let datas = [];
    for (let key in data) {
      let splitted = key.split(",");
      let lat = parseFloat(splitted[0]);
      let lon = parseFloat(splitted[1]);
      console.log(data[key][index]);
      console.log(typeof data[key][index]);
      let is_free = data[key][index] === 0 ? true : false;
      if (is_free === true) {
        datas.push([lat, lon, 0.7]);
      }
    }
    heat = L.heatLayer(datas, {maxZoom: 14}).addTo(map);
    index++;
  }, 1000);
};
