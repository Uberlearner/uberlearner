require(['jquery', 'jquery-ui', 'css!lib/jquery_ui/css/jquery-ui', 'bootstrap'], function($) {
    $(function(){
        $('.date-widget').datepicker({
            dateFormat: 'yy-mm-dd',
            changeMonth: true,
            changeYear: true,
            yearRange: '-90:+0'
        });
    });
});
