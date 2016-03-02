{% load i18n %}

<script type="text/javascript">
  $(function(){
      $('#{{ form_id }} select[data-ajax--url]').select2();

      $('#{{ form_id }}').find('select, input').change(function() {
          ecs.stopPageLoad();
          $('#{{ form_id }}').submit();
      });

      var threshold = 7;

      var toggle_collapse = function(){
          var toggler = $(this);
          var item = toggler.parent();
          var lis = item.find('ul li');
          if(item.hasClass('collapsed')) {
              toggler.html('{% trans "Collapse" %}');
              lis.show();
              lis.filter(':last-child').hide();
          } else {
              toggler.html('{% trans "Expand" %}');
              lis.slice(threshold).hide();
              lis.filter(':last-child').show();
          }
          item.toggleClass('collapsed');
      };
      $('#task_main .task_item.toggle_collapse').each(function() {
          var item = $(this);

          if (item.find('ul li').length <= threshold) {
              return;
          }

          var toggler = $('<a/>', {
              on: {
                  click: toggle_collapse
              },
              style: 'float: right;'
          });
          item.prepend(toggler);

          var ellipsis = $('<li>&hellip;</li>');
          item.find('ul').append(ellipsis);

          toggle_collapse.apply(toggler);
      });
      
      ecs.setupSubmitLinks('a.submit_parent');
});
</script>

