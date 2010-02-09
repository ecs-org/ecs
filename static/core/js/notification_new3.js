// notification_new3.js

/*
 * tabs
 */
$(function() {
  $("#ecs-core-tabs").tabs({ disabled: [0, 1], selected: 2 });
});

/*
 * lists
 */
$(function() {
  $("#ecs-core-selectable1").selectable();
  $("#ecs-core-selectable2").selectable();
});

/*
 * date picker
 */
$(function() {
  // TODO European Date Format
  // TODO Button images?
  $("#ecs-core-datepicker").datepicker();
});
