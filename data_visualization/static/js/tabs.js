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
    datatype: "json"
  }).done(function(data) {
      html = json_to_html_table(data, null, true, true, true)[0].join(" ");
      $("#user_data").empty();
      $("#user_data").append(html);
  });
};

var load_sensors = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/sensors",
    type: "GET",
    datatype: "json"
  }).done(function(data) {
    let [html, markers, paths] = json_to_html_table(data, null, true, true, true);
    let requests = []

    for (let idx = 0; idx < markers.length; idx++) {
      requests.push($.ajax({
        url: $SCRIPT_ROOT + paths[idx],
        type: "GET",
        datatype: "json"
      }).done(function(data) {
        html[markers[idx]] = "<td>" + data["name"] + "</td>";
      }));
    }

    $.when.apply(null, requests).done(function() {
      html = html.join(" ");
      $("#user_data").empty();
      $("#user_data").append(html);
    });
  });
};

var load_views = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/views",
    type: "GET",
    datatype: "json"
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
      datatype: "json"
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
        datatype: "json"
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
};

var load_tab = function(name) {
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
    default:
      break;
  }
};
