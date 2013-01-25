define(['jquery'], function() {
    $(function() {
        if ($('#ko_uberGrid_sortingOptions').length == 0) {
            $('body').append(
                '<script type="text/html" id="ko_uberGrid_sortingOptions">' +
                    '<div class="row" data-bind="visible: showSortingOptions()">' +
                    '<div class="span2 pull-left">' +
                        '<label> Sort by:' +
                            '<select data-bind="options: sortingOptions, optionsText: \'name\', value: changeSortingOption">' +
                            '</select>' +
                        '</label>' +
                    '</div>' +
                    '</div>' +
                '</script>'
            );
        }
    });
});
