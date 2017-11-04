var play_chart = function() {
  request_data = {};
  $("canvas[id^='chart']").each(function() {
    let key = $(this).attr("id");
    request_data[key] = chart_data_lengths[key];
  });
  $.ajax({
    url: $SCRIPT_ROOT + "/charts/" + dynamic_view["view_id"] + "/refresh",
    type: "GET",
    datatype: "json",
    data: request_data,
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    $("canvas[id^='chart']").each(function() {
      let $this = $(this);
      let refresh_data = data[$this.attr("id")];
      let data_length = chart_data_lengths[$this.attr("id")];

      for (let i = 0; i < refresh_data.length; i++) {
        window[$this.attr("id")].data.labels[data_length] = refresh_data[i]["timestamp"];
        window[$this.attr("id")].data.datasets[0].data[data_length] = refresh_data[i]["value"];
        data_length++;
      }
      chart_data_lengths[$this.attr("id")] = data_length;
      window[$this.attr("id")].update();
    });
  });
}

var play_view = function() {
  request_data = {};
  $("canvas").each(function() {
    let key = $(this).attr("id");
    request_data[key] = chart_data_lengths[key];
  });
  $.ajax({
    url: links[link_index]["charts_refresh"],
    type: "GET",
    data: request_data,
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    $("canvas").each(function() {
      let $this = $(this);
      let refresh_data = data[$this.attr("id")];
      let data_length = chart_data_lengths[$this.attr("id")];

      if (view_type == "normal") {
        for (let i = 0; i < refresh_data.length; i++) {
          window[$this.attr("id")].data.labels[data_length] = refresh_data[i]["timestamp"];
          window[$this.attr("id")].data.datasets[0].data[data_length] = refresh_data[i]["value"];
          data_length++;
        }
        chart_data_lengths[$this.attr("id")] = data_length;
        window[$this.attr("id")].update();
      } else if (view_type == "preconfigured") {
        if (replay_interval_id != null) {
          clearInterval(replay_interval_id);
          replay_interval_id = null;
        }
        setTimeout(function() {
          datareplay($this.attr("id"), refresh_data, chart_data_lengths);
        }, 0);
      }
    });
  });
}

var play_map = function() {
  refresh_data = {};
  $.ajax({
    url: user_links["map_refresh"],
    type: "GET",
    datatype: "json",
    data: {"map": map_last_index},
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    let map_last_index_set = false;
    let replay_data = {};
    for (let key in data) {
      if (!map_last_index_set) {
        map_last_index += data[key].length;
        map_last_index_set = true;
      }
      replay_data[key] = [];
      for (let i = 0; i < data[key].length; i++) {
        replay_data[key].push(data[key][i]["value"]);
      }
    }
    if (replay_interval_id != null) {
      clearInterval(replay_interval_id);
      replay_interval_id = null;
    }
    setTimeout(function() {
      replay(replay_data);
    }, 0);
  });
};
