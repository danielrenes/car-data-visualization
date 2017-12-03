var load_modal = function(data) {
  let title = $(data).filter(".title").text();
  let html_form = $(data).filter(".loaded_content");
  let cta = $(data).filter("button");

  $(".modal-card-title").empty().append(title);
  $(".modal-card-body").empty().append(html_form);
  $(".modal-card-foot > button.button").replaceWith(cta);
  $(".modal").addClass("is-active");
};

var load_categories = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/categories",
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
      html = json_to_html_table(data, null, true, true, true)[0].join(" ");
      $("#user_data").empty();
      $("#user_data").append(html);

      if (data["categories"].length == 0) {
        links.push(user_links["_fallback"]["categories"]);
      }
  });
};

var load_sensors = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/sensors",
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    let [html, markers, paths] = json_to_html_table(data, null, true, true, true);
    let requests = []

    for (let idx = 0; idx < markers.length; idx++) {
      requests.push($.ajax({
        url: $SCRIPT_ROOT + paths[idx],
        type: "GET",
        datatype: "json",
        beforeSend: function(request) {
          request.setRequestHeader("Authorization", get_authorization());
        }
      }).done(function(data) {
        html[markers[idx]] = "<td>" + data["name"] + "</td>";
      }));
    }

    $.when.apply(null, requests).done(function() {
      html = html.join(" ");
      $("#user_data").empty();
      $("#user_data").append(html);
    });

    if (data["sensors"].length == 0) {
      links.push(user_links["_fallback"]["sensors"]);
    }
  });
};

var load_views = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/views",
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    html = json_to_breadcrumb(data);
    $("#user_data").empty();
    $("#user_data").append(html);

    if (active_breadcrumb != null) {
      link_index = active_breadcrumb;
      let $this = $("nav.breadcrumb > ul > li").eq(active_breadcrumb);
      $this.siblings().removeClass("is-active");
      $this.addClass("is-active");
      load_subviews(active_breadcrumb);
    }

    if (data["views"].length == 0) {
      links.push(user_links["_fallback"]["views"]);
    }
  });
};

var load_subviews = function(view_idx) {
  let subview_links = links[view_idx]["subviews"];
  let requests = [];
  let datas = {};
  datas["subviews"] = [];

  for (let idx = 0; idx < subview_links.length; idx++) {
    requests.push($.ajax({
      url: $SCRIPT_ROOT + subview_links[idx],
      type: "GET",
      datatype: "json",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", get_authorization());
      }
    }).done(function(data) {
      filtered_data = {};
      for (let key in data) {
        if (key.indexOf("view") != -1) {
          continue;
        } else {
          filtered_data[key] = data[key];
        }
      }
      datas["subviews"].push(filtered_data);
    }));
  }

  $.when.apply(null, requests).done(function() {
    let [html, markers, paths] = json_to_html_table(datas, null, true, true, true);
    let requests2 = [];

    for (let idx = 0; idx < markers.length; idx++) {
      requests2.push($.ajax({
        url: $SCRIPT_ROOT + paths[idx],
        type: "GET",
        datatype: "json",
        beforeSend: function(request) {
          request.setRequestHeader("Authorization", get_authorization());
        }
      }).done(function(data) {
        let value = "n/a";

        for (let key in data) {
          if (key == "name") {
            value = data[key];
            break;
          } else if (key == "type") {
            value = data[key];
          }
        }

        html[markers[idx]] = "<td>" + value + "</td>";
      }));
    }

    $.when.apply(null, requests2).done(function() {
      html = html.join(" ");
      $(".loaded_content").remove();
      $("#user_data").append(html);
    });
  });

  if (subview_links.length == 0) {
    console.log(links[view_idx]);
    sublinks.push(links[view_idx]["_fallback"]["subviews"]);
  }
};

var load_map = function() {
  map_last_index = 0;
  heat = null;

  $.ajax({
    url: user_links["map_init"],
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    $("#user_data").empty();
    $("#user_data").append("<div style='width: 800px; height: 500px; margin-left: auto; margin-right: auto' id='map'></div>");
    map = L.map("map").setView([data["center"]["latitude"], data["center"]["longitude"]], data["zoom"]);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    play_map();
    interval_id = setInterval(play_map, 60000);
  });
};

var load_tab = function(name) {
  if (replay_interval_id != null) {
    clearInterval(replay_interval_id);
    replay_interval_id = null;
  }
  switch (name) {
    case 'categories':
      load_categories();
      link_index = null;
      break;
    case 'sensors':
      load_sensors();
      link_index = null;
      break;
    case 'views':
      load_views();
      break;
    case 'map':
      load_map();
      link_index = null;
      break;
    default:
      break;
  }
};
