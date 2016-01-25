{% load i18n %}

<script type="text/javascript">
  jQuery(function(){
      jQuery('#{{ form_id }} select[data-ajax--url]').select2();

      jQuery('#{{ form_id }}').find('select, input').change(function() {
          ecs.stopPageLoad();
          jQuery('#{{ form_id }}').submit();
      });

      var threshold = 7;

      var toggle_collapse = function(){
          var toggler = jQuery(this);
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
      jQuery('#task_main .task_item.toggle_collapse').each(function() {
          var item = jQuery(this);

          if (item.find('ul li').length <= threshold) {
              return;
          }

          var toggler = jQuery('<a/>', {
              on: {
                  click: toggle_collapse
              },
              style: 'float: right;'
          });
          item.prepend(toggler);

          var ellipsis = jQuery('<li>&hellip;</li>');
          item.find('ul').append(ellipsis);

          toggle_collapse.apply(toggler);
      });
      
      ecs.setupSubmitLinks('a.submit_parent');
});
</script>

