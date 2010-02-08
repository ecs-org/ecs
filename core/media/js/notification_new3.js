// notification_new3.js

/*
 * tabs
 */
$(function() {
  $("#tabs").tabs({ disabled: [0, 1], selected: 2 });
});

/*
 * lists
 */
$(function() {
  $("#selectable1").selectable();
  $("#selectable2").selectable();
});

/*
 * date picker
 */
$(function() {
  // TODO European Date Format
  // TODO Button images?
  $("#datepicker").datepicker();
});
