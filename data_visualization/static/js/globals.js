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

var popup_keep_open = false;
