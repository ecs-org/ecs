{% load i18n %}

<script type="text/javascript">
  window.addEvent('domready', function(){
      $$('#{{ form_id }} input').each(function(input){
          input.addEvent('change', function(){
              $('{{ form_id }}').submit();
          });
      });
      $$('#{{ form_id }} select').each(function(input){
          input.addEvent('change', function(){
              $('{{ form_id }}').submit();
          });
      });
      $$('#{{ form_id }} a[bookmarktitle]').each(function(a){
          a.addEvent('click', function(){
              var title = a.getAttribute('bookmarktitle');
              var url = a.getAttribute('href');
              return !ecs.bookmark(url, title);
          });
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
  });
</script>

