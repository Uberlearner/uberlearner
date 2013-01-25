define(['jquery'], function($) {
    $(function() {
        if ($('#ko_uberGrid_grid').length == 0) {
            $('body').append(
                '<script type="text/html" id="ko_uberGrid_grid">' +
                    '<div class="row">' +
                        '<table class="table table-striped table-bordered" data-bind="visible: dataExists">' +
                            '<thead>' +
                                '<tr data-bind="foreach: columns">' +
                                    '<th data-bind="text: $data.headerText"></th>' +
                                '</tr>' +
                            '</thead>' +
                            '<tbody data-bind="foreach: currentData">' +
                                '<tr data-bind="foreach: $root.columns">' +
                                    '<td data-bind="html: $root.getDataHtml($parentContext.$data, $data)">' +
                                    '</td>' +
                                '</tr>' +
                            '</tbody>' +
                        '</table>' +
                    '</div>' +
                '</script>'
            );
        }
    });
});