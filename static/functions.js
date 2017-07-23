$(document).ready(function() {
  var get_cookie = function(searchKey) {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      let [key, value] = cookies[i].split("=");
      while (key.charAt(0) == " ") {
        key = key.substring(1);
      }
      if (key == searchKey) {
        return value;
      }
    }
    return null;
  };

  var active_tab_from_cookie = get_cookie("active_tab");
  var active_breadcrumb_from_cookie = get_cookie("active_breadcrumb");

  var active_tab = active_tab_from_cookie == null ? "info" : active_tab_from_cookie;
  var active_breadcrumb = active_breadcrumb_from_cookie == null ? null : get_cookie("active_breadcrumb");

  var links = [];
  var sublinks = [];
  var last_link = null;
  var link_index = null;
  var interval_id = null;
  var chart_data_lengths = {};
  var refresh_time = null;

  var json_to_html_table = function(data, message, modifiable, push_links, use_markers) {
    if (push_links) {
      if (link_index == null) {
        links.length = 0;
      } else {
        sublinks.length = 0;
      }
    }

    let html = [];
    let markers = [];
    let paths = [];

    for (let key in data) {
      data = data[key];
      break;
    }

    html.push("<div class='loaded_content'>");
    if (message != null) {
      html.push("<div class='notification is-warning'>", message, "</div>");
    }
    html.push("<table class='table'>", "<thead>", "<tr>");

    if (data.length > 0) {
      let obj = data[0];
      for (let key in obj) {
        if (key == "id" || key == 'links') {
          continue;
        } else if (key.indexOf("id") != -1) {
          if (use_markers) {
            key = key.split("id")[0] + "name";
            html.push("<th>" + key + "</th>");
          }
        } else {
          html.push("<th>" + key + "</th>");
        }
      }
    }

    if (modifiable) {
      html.push("<th class='is-narrow'>", "<span class='icon add'>",
          "<i class='fa fa-plus-square'>", "</i>", "</span>", "</th>");
    }

    html.push("</tr>", "</thead>", "<tbody>");

    for (let i = 0; i < data.length; i++) {
      let obj = data[i];
      html.push("<tr>");
      for (let key in obj) {
        if (key == "id") {
          continue;
        } else if (key == "links") {
          if (push_links) {
            if (link_index == null) {
              links.push(obj[key]);
            } else {
              sublinks.push(obj[key]);
            }
          }
        } else if (key.indexOf("id") != -1) {
          if (use_markers) {
            markers.push(html.length);
            paths.push(obj["links"][key.split("_id")[0]]);
            html.push("<td></td>");
          }
        } else {
          let value = obj[key];
          if (value == null || value == "") {
            value = "n/a";
          }
          html.push("<td>" + value + "</td>");
        }
      }

      if (modifiable) {
        html.push("<td class='is-narrow'>");
        html.push("<span class='icon edit'>", "<i class='fa fa-pencil-square-o'>", "</i>", "</span>");
        html.push("<span class='icon remove'>", "<i class='fa fa-minus-square'>", "</i>", "</span>");
        html.push("</td>");
      }

      html.push("</tr>");
    }

    html.push("</tbody>", "</table>", "</div>");

    return [html, markers, paths];
  };

  var json_to_breadcrumb = function(data) {
    links.length = 0;

    let html = [];

    for (let key in data) {
      data = data[key];
      break;
    }

    html.push("<nav class='breadcrumb is-centered'>", "<ul>");

    for (let i = 0; i < data.length; i++) {
      let obj = data[i];
      let title = null;
      let icon_href = null;
      for (let key in obj) {
        if (key == "name") {
          title = obj[key];
        } else if (key == "links") {
          let obj_links = obj[key];
          links.push(obj_links);
          for (let key2 in obj_links) {
            if (key2 == "icon") {
              icon_href = obj_links[key2];
            }
          }
        }
      }

      if (title != null && icon_href != null) {
        html.push("<li>", "<a>", "<span class='icon is-small'>", "<img src='" + icon_href + "'>", "</img>", "</span>", "<span>", title, "</span>", "</span>", "</a>", "</li>");
      }
    }

    html.push("</ul>", "</nav>");

    return html.join("");
  };

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

  $(".tabs > ul > li").each(function() {
    let $this = $(this);
    if ($this.text().toLowerCase() == active_tab) {
      $this.siblings().removeClass("is-active");
      $this.addClass("is-active");
      load_tab(active_tab);
    }
  });

  $(".tabs > ul > li").click(function() {
    if (interval_id != null) {
      clearInterval(interval_id);
      interval_id = null;
    }
    let $this = $(this);
    $this.siblings().removeClass("is-active");
    $this.addClass("is-active");
    active_tab = $this.text().toLowerCase();
    active_breadcrumb = null;
    document.cookie = "active_tab=" + active_tab;
    document.cookie = "active_breadcrumb=" + active_breadcrumb;
    load_tab(active_tab);
  });

  $(document.body).on("click", "span.icon.add", function() {
    let uselink = links[0];

    if ($("nav.breadcrumb").length && $(this).closest("div").attr("class") == "loaded_content") {
      uselink = sublinks[0];
    }

    $.ajax({
      url: uselink["form_add"],
      type: "GET",
      datatype: "html"
    }).done(function(data) {
      load_modal(data);
    });
  });

  $(document.body).on("click", "span.icon.edit", function() {
    let uselink = links;
    let index = $("span.icon.edit").index($(this));

    if ($("nav.breadcrumb").length && $(this).closest("div").attr("class") == "loaded_content") {
      uselink = sublinks;
    }

    if (link_index != null && $(this).closest("div").attr("class") == "mod_popup") {
      index = link_index;
    }

    $.ajax({
      url: uselink[index]["form_edit"],
      type: "GET",
      datatype: "html"
    }).done(function(data) {
        load_modal(data);
    });
  });

  $(document.body).on("click", "span.icon.remove", function() {
    let uselink = links;
    let index = $("span.icon.remove").index($(this));

    if ($("nav.breadcrumb").length && $(this).closest("div").attr("class") == "loaded_content") {
      uselink = sublinks;
    }

    if (link_index != null && $(this).closest("div").attr("class") == "mod_popup") {
      index = link_index;

      $.ajax({
        url: uselink[index]["self"],
        type: "DELETE",
        datatype: "json"
      }).done(function() {
        load_tab(active_tab);
      });
    }

    $.ajax({
      url: uselink[index]["self"],
      type: "GET",
      datatype: "json"
    }).done(function(data) {
      let self = data["name"];
      let link_for = null;
      for (let key in uselink[index]) {
        if (key != "self" && key != "icon" && !key.includes("form")) {
          let found = false;
          for (let key2 in data) {
            if (key2.includes(key)) {
              found = true;
              break;
            }
          }
          if (!found) {
            link_for = key;
            break;
          }
        }
      }

      if (link_for != null) {
        let requests = [];
        let deleted_objs = {};
        deleted_objs["deleted"] = [];

        uselink[index][link_for].forEach(function(link) {
          requests.push($.ajax({
            url: link,
            type: "GET",
            datatype: "json"
          }).done(function(data) {
            deleted_objs["deleted"].push(data);
          }));
        });

        $.when.apply(null, requests).done(function() {
          if (deleted_objs["deleted"].length > 0) {
            message = ["If you delete<strong>", self, "</strong>the following<strong>", link_for,
                "</strong>will be lost!<br>Press confirm if you want to delete it anyways!"];
            html = json_to_html_table(deleted_objs, message.join(" "), false, false, false)[0];
            html.push("<p class='title'>", "Warning", "</p>");
            html.push("<button class='button is-warning remove_confirmed'>", "Confirm", "</button>");
            load_modal(html.join(" "));
            last_link = uselink[index]["self"];
          } else {
            $.ajax({
              url: uselink[index]["self"],
              type: "DELETE",
              datatype: "json"
            }).done(function() {
              load_tab(active_tab);
            });
          }
        });
      } else {
        $.ajax({
          url: uselink[index]["self"],
          type: "DELETE",
          datatype: "json"
        }).done(function() {
          load_tab(active_tab);
        });
      }
    });
  });

  $(document.body).on("click", "button.redirect", function () {
    document.cookie = "active_tab=" + active_tab;
    document.cookie = "active_breadcrumb=" + active_breadcrumb;
  });

  $(document.body).on("click", "button.remove_confirmed", function() {
    $.ajax({
      url: last_link,
      type: "DELETE",
      datatype: "json"
    }).done(function() {
      load_tab(active_tab);
      last_link = null;
      $(".modal").removeClass("is-active");
    });
  });

  $(document.body).on("click", "nav.breadcrumb > ul > li", function() {
    let $this = $(this);
    if (active_tab == "views" && !$this.hasClass('is-active')) {
      if (interval_id != null) {
        clearInterval(interval_id);
        interval_id = null;
      }
      let index = $("nav.breadcrumb > ul > li").index($this);
      active_breadcrumb = index;
      document.cookie = "active_breadcrumb=" + active_breadcrumb;
      load_subviews(index);
      $this.siblings().removeClass("is-active");
      $this.addClass("is-active");
      let offset = $(this).offset();
      $(".mod_popup").css("left", (offset.left + 15) + "px");
      $(".mod_popup").css("top", (offset.top + 35) + "px");
      $(".mod_popup").css("visibility", "visible");
      $(".mod_popup").css("opacity", "1");
    }
  });

  $(document.body).on("mouseenter", "nav.breadcrumb > ul > li", function() {
    link_index = $("nav.breadcrumb > ul > li").index($(this));
    if (active_breadcrumb == link_index) {
      let offset = $(this).offset();
      setTimeout(function() {
        $(".mod_popup").css("left", (offset.left + 15) + "px");
        $(".mod_popup").css("top", (offset.top + 35) + "px");
        $(".mod_popup").css("visibility", "visible");
        $(".mod_popup").css("opacity", "1");
      }, 100);
    }
  });

  var popup_keep_open = false;

  $(document.body).on("mouseleave", "nav.breadcrumb > ul > li", function() {
    setTimeout(function() {
      if (!popup_keep_open) {
        $(".mod_popup").css("opacity", "0");
        $(".mod_popup").css("visibility", "hidden");
      }
    }, 100);
  });

  $(document.body).on("mouseenter", ".mod_popup", function() {
    popup_keep_open = true;
  });

  $(document.body).on("mouseleave", ".mod_popup", function() {
    popup_keep_open = false;
    $(".mod_popup").css("opacity", "0");
    $(".mod_popup").css("visibility", "hidden");
  });

  $(document.body).on("click", "span.icon.play", function() {
    $.ajax({
      url: links[link_index]["self"],
      type: "GET",
      datatype: "json"
    }).done(function(data) {
      refresh_time = data["refresh_time"] * 1000;
      $.ajax({
        url: links[link_index]["charts_init"],
        type: "GET",
        datatype: "html"
      }).done(function(data) {
        if ($(".loaded_content").length) {
          $(".loaded_content").remove();
        }
        $("#user_data").append(data);
        chart_data_lengths = {};
        $("canvas").each(function() {
          chart_data_lengths[$(this).attr("id")] = 0;
        });
        interval_id = setInterval(function() {
          request_data = {};
          $("canvas").each(function() {
            let key = $(this).attr("id");
            request_data[key] = chart_data_lengths[key];
          });
          $.ajax({
            url: links[link_index]["charts_refresh"],
            type: "GET",
            data: request_data,
            datatype: "json"
          }).done(function(data) {
            $("canvas").each(function() {
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
        }, refresh_time);
      });
    });
  });

  $(".modal-card > header > .delete").add(".modal-card > footer > a").click(function() {
    last_link = null;
    $(".modal").removeClass("is-active");
  });
});
