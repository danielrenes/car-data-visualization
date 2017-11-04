var fn_login = function() {
  window.localStorage.setItem("username", window.btoa($("#username").val()));
  window.localStorage.setItem("password", window.btoa($("#password").val()));
}

var fn_close_user_menu = function() {
  $(".menu").removeClass("opened");
}

var fn_handle_user_menu = function(e) {
  $(".menu").toggleClass("opened");
  e.stopPropagation();
}

var fn_edit_account = function() {
  $.ajax({
    url: user_links["form_edit"],
    type: "GET",
    datatype: "html"
  }).done(function(data) {
    load_modal(data);
  });
}

var fn_find_active_tab = function() {
  let $this = $(this);
  if ($this.text().toLowerCase() == active_tab) {
    $this.siblings().removeClass("is-active");
    $this.addClass("is-active");
    load_tab(active_tab);
  }
};

var fn_select_tab = function() {
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
};

var fn_close_modal = function() {
  last_link = null;
  if (dynamic_view != null) {
    $.ajax({
      url: $SCRIPT_ROOT + "/view/dynamic/remove",
      type: "GET",
      datatype: "json",
      data: dynamic_view,
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", get_authorization());
      }
    }).done(function(data) {
      dynamic_view = null;
    });
    if (interval_id != null) {
      clearInterval(interval_id);
      interval_id = null;
    }
  }
  $(".modal").removeClass("is-active");
};

var fn_icon_add = function() {
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
};

var fn_icon_edit = function() {
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
};

var fn_icon_remove = function() {
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
      datatype: "json",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", get_authorization());
      }
    }).done(function() {
      load_tab(active_tab);
    });
  }

  $.ajax({
    url: uselink[index]["self"],
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
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
          datatype: "json",
          beforeSend: function(request) {
            request.setRequestHeader("Authorization", get_authorization());
          }
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
        datatype: "json",
        beforeSend: function(request) {
          request.setRequestHeader("Authorization", get_authorization());
        }
      }).done(function() {
        load_tab(active_tab);
      });
    }
  });
};

var fn_button_redirect = function () {
  document.cookie = "active_tab=" + active_tab;
  document.cookie = "active_breadcrumb=" + active_breadcrumb;
};

var fn_button_remove_confirmed = function() {
  $.ajax({
    url: last_link,
    type: "DELETE",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function() {
    load_tab(active_tab);
    last_link = null;
    $(".modal").removeClass("is-active");
  });
};

var fn_select_breadcrumb = function() {
  let $this = $(this);
  if (active_tab == "views" && !$this.hasClass('is-active')) {
    if (interval_id != null) {
      clearInterval(interval_id);
      interval_id = null;
    }
    let index = $("nav.breadcrumb > ul > li").index($this);
    active_breadcrumb = index;
    document.cookie = "active_breadcrumb=" + active_breadcrumb;
    $.ajax({
      url: links[index]["self"],
      type: "GET",
      datatype: "json",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", get_authorization());
      }
    }).done(function(data) {
      view_type = data["type"];
      if (view_type == "normal") {
        load_subviews(index);
      }
    });
    $this.siblings().removeClass("is-active");
    $this.addClass("is-active");
    let offset = $(this).offset();
    $(".mod_popup").css("left", (offset.left + 15) + "px");
    $(".mod_popup").css("top", (offset.top + 35) + "px");
    $(".mod_popup").css("visibility", "visible");
    $(".mod_popup").css("opacity", "1");
  }
};

var fn_enter_breadcrumb = function() {
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
};

var fn_leave_breadcrumb = function() {
  setTimeout(function() {
    if (!popup_keep_open) {
      $(".mod_popup").css("opacity", "0");
      $(".mod_popup").css("visibility", "hidden");
    }
  }, 100);
};

var fn_enter_mod_popup = function() {
  popup_keep_open = true;
};

var fn_leave_mod_popup = function() {
  popup_keep_open = false;
  $(".mod_popup").css("opacity", "0");
  $(".mod_popup").css("visibility", "hidden");
};

var fn_icon_play = function() {
  $.ajax({
    url: links[link_index]["self"],
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    refresh_time = data["refresh_time"] * 1000;
    $.ajax({
      url: links[link_index]["charts_init"],
      type: "GET",
      datatype: "html",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", get_authorization());
      }
    }).done(function(data) {
      if ($(".loaded_content").length) {
        $(".loaded_content").remove();
      }
      $("#user_data").append(data);
      chart_data_lengths = {};
      $("canvas").each(function() {
        chart_data_lengths[$(this).attr("id")] = 0;

        // hack to display canvas-gauges
        let data_type = $(this).attr("data-type");
        if (typeof data_type !== typeof undefined && data_type !== false) {
          let attr_copy = $(this).attr("data-type");
          $(this).attr("data-type", "");
          $(this).attr("data-type", attr_copy);
        }
      });

      $.ajax({
        url: links[link_index]["self"],
        type: "GET",
        datatype: "json",
        beforeSend: function(request) {
          request.setRequestHeader("Authorization", get_authorization());
        }
      }).done(function(data) {
        view_type = data["type"];
        play_view();
        interval_id = setInterval(play_view, refresh_time);
      });
    });
  });
};

var fn_gauge_data = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/view/dynamic/add",
    type: "GET",
    datatype: "json",
    data: {
      sensor_name: $(this).attr("id")
    },
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    dynamic_view = data;
    $.ajax({
      url: $SCRIPT_ROOT + "/charts/" + dynamic_view["view_id"],
      type: "GET",
      datatype: "html",
      beforeSend: function(request) {
        request.setRequestHeader("Authorization", get_authorization());
      }
    }).done(function(data) {
      load_modal(data);
      $(".modal-card").css("width", "1200px");
      $(".charts_wrap > .column").css("width", "1000px");
      chart_data_lengths = {};
      $("canvas[id^='chart']").each(function() {
        chart_data_lengths[$(this).attr("id")] = 0;
      });
      if (interval_id != null) {
        clearInterval(interval_id);
        clearInterval(replay_interval_id);
      }
      play_chart();
      interval_id = setInterval(play_chart, 10000);
    });
  });
};
