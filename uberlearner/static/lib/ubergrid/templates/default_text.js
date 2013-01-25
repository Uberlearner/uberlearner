define(['jquery'], function($) {
    $(function() {
        if ($('#ko_uberGrid_defaultText').length == 0) {
            $('body').append(
                '<script type="text/html" id="ko_uberGrid_defaultText">' +
                    '<div class="row" data-bind="visible: !dataExists()">' +
                        '<p data-bind="text: defaultText"></p>' +
                    '</div>' +
                '</script>'
            );
        }
    });
});
