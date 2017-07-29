$(document).ready(function() {
  $(".tabs > ul > li").each(fn_find_active_tab);
  $(".tabs > ul > li").click(fn_select_tab);
  $(".modal-card > header > .delete").add(".modal-card > footer > a").click(fn_close_modal);
  $(document.body).on("click", "span.icon.add", fn_icon_add);
  $(document.body).on("click", "span.icon.edit", fn_icon_edit);
  $(document.body).on("click", "span.icon.remove", fn_icon_remove);
  $(document.body).on("click", "button.redirect", fn_button_redirect);
  $(document.body).on("click", "button.remove_confirmed", fn_button_remove_confirmed);
  $(document.body).on("click", "nav.breadcrumb > ul > li", fn_select_breadcrumb);
  $(document.body).on("mouseenter", "nav.breadcrumb > ul > li", fn_enter_breadcrumb);
  $(document.body).on("mouseleave", "nav.breadcrumb > ul > li", fn_leave_breadcrumb);
  $(document.body).on("mouseenter", ".mod_popup", fn_enter_mod_popup);
  $(document.body).on("mouseleave", ".mod_popup", fn_leave_mod_popup);
  $(document.body).on("click", "span.icon.play", fn_icon_play);
});
