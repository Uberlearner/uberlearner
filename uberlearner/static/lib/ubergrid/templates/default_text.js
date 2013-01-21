define(['jquery'], function($) {
    $(function() {
        $('body').append('<script type="text/html" id="ko_uberGrid_defaultText">' +
            '<div class="row" data-bind="visible: !dataExists()">' +
                '<p data-bind="text: defaultText"></p>' +
            '</div>' +
        '</script>'
        );
    });
});
