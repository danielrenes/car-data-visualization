/**
 * Copy credidentials to object.
 */
var get_user = function() {
  user["username"] = window.localStorage.getItem("username");
  user["password"] = window.localStorage.getItem("password");
}

/**
 * Get authentication token.
 */
var get_token = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/token",
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", "Basic " + get_username_password());
    }
  }).done(function(data) {
    user["token"] = data["token"];
    let expiration = new Date();
    expiration.setSeconds(expiration.getSeconds() + data["expiration"]);
    console.log("token expires at: " + expiration);
    user["expiration"] = expiration;
  });
};

/**
 * Returns the username:password or token credidentials to be able to communicate with the API.
 * @return {String} credidentials
 */
var get_authorization = function() {
  if ("token" in user) {
    let token = user["token"];
    let now = new Date();
    if (now < user["expiration"]) {
      return "Basic " + window.btoa(token + ":");
    } else {
      get_token();
      return "Basic " + get_username_password();
    }
  } else {
    return "Basic " + get_username_password();
  }
};

/**
 * Returns username:password credidentials to be able to communicate with the API.
 * @return {String} credidentials
 */
var get_username_password = function() {
  let username = null;
  let password = null;
  if ("username" in user) {
    username = window.atob(user["username"]);
    password = window.atob(user["password"]);
  } else {
    username = window.localStorage.getItem("username");
    password = window.localStorage.getItem("password");
    user["username"] = username;
    user["password"] = password;
  }
  return window.btoa(username + ":" + password);
};

/**
 * Load the links associated with the user account.
 */
var get_user_links = function() {
  $.ajax({
    url: $SCRIPT_ROOT + "/user",
    type: "GET",
    datatype: "json",
    beforeSend: function(request) {
      request.setRequestHeader("Authorization", get_authorization());
    }
  }).done(function(data) {
    user_links = data["links"];
  });
};

/**
 * Find cookie value for the given search key.
 * @param {String} searchKey key for the cookie
 * @return {String} the cookie value for the key or null if there is no cookie with the given key
 */
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

/**
 * Creates HTML table with Bulma CSS styles from JSON data.
 * @param {String} data JSON data
 * @param {String} message (optional) warning message
 * @param {Boolean} modifiable place modification items
 * @param {Boolean} push_links replace links
 * @param {Boolean} use_markers mark resolvable fields
 * @return {Array} array with the html table, the markers for the resolvable fields and paths for the requests to resolve the fields
 */
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

/**
 * Create HTML breadcrumb with Bulma CSS styles from JSON data.
 * @param {String} data JSON data
 * @return {String} HTMl breadcrumb
 */
var json_to_breadcrumb = function(data) {
  links.length = 0;

  let html = [];

  for (let key in data) {
    data = data[key];
    break;
  }

  if (data.length == 0) {
    html.push("<span class='icon add'>", "<i class='fa fa-plus-square'>", "</i>", "</span>");
  } else {
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
        html.push("<li>", "<a>", "<span class='icon is-small'>", "<img src='" + icon_href + "'>", "</img>", "</span>", "<span>", title, "</span>", "</a>", "</li>");
      }
    }

    html.push("</ul>", "</nav>");
  }

  return html.join("");
};

var datareplay = function(element_id, data, chart_data_lengths) {
  let index = 0;
  let gauge = document.gauges.get(element_id);
  setInterval(function() {
    gauge.value = data[index]["value"];
    index++;
    chart_data_lengths[element_id] = index;
  }, 1000);
};
