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
          var item = this.getParent();
          var lis = item.getElement('ul').getElements('li');
          if(item.hasClass('collapsed')) {
              this.innerHTML = '{% trans "Collapse" %}';
              lis.show();
              lis.pop().hide();
          } else {
              this.innerHTML = '{% trans "Expand" %}';
              lis.splice(0, threshold);
              lis.hide();
              lis.pop().show();
          }
          item.toggleClass('collapsed');
      };
      $$('#task_main .task_item.toggle_collapse').each(function(item){
          if (item.getElement('ul').getElements('li').length <= threshold) {
              return;
          }
          var toggler = new Element('a', {
              'text': 'foo',
              'events': {
                  'click': toggle_collapse
              },
              'styles': {
                  'float': 'right'
              }
          });
          item.insertBefore(toggler, item.getFirst());
          var elipsis = new Element('li', {
              'text': '...'
          });
          elipsis.inject(item.getElement('ul'));
          toggle_collapse.apply(toggler);
      });
      
      ecs.setupSubmitLinks('a.submit_parent');
});
</script>

