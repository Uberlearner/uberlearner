define(['jquery'], function() {
    $(function() {
        $('body').append(
            '<script type="text/html" id="ko_uberGrid_pageLinks">' +
                '<div class="row" data-bind="visible: dataExists() && maxPageIndex() > 0">' +
                    '<div class="span2">' +
                        '<a href="javascript: void(0);" data-bind="visible: hasPrevious,	click: function() { currentPageIndex(0) }">' +
                        'First' +
                        '</a>' +
                        '<a href="javascript: void(0);" data-bind="visible: hasPrevious, click: function() { currentPageIndex(currentPageIndex()-1) }">' +
                        'Previous' +
                        '</a>' +
                    '</div>' +
                    '<div class="span4">' +
                    '<ul class="nav nav-pills" data-bind="foreach: pageIndexes">' +
                        '<li data-bind="css: { active: $data == $root.currentPageIndex() }">' +
                            '<a href="javascript: void(0);"data-bind="click: function() { $root.currentPageIndex($data) }, text: $data + 1"> </a>' +
                        '</li>' +
                    '</ul>' +
                    '</div>' +
                    '<div class="span2">' +
                        '<span class="pull-right">' +
                            '<a href="javascript: void(0);" data-bind="visible: hasNext,	click: function() { currentPageIndex(currentPageIndex()+1) }">' +
                            'Next' +
                            '</a>' +
                            '<a href="javascript: void(0);" data-bind="visible: hasNext, click: function() { currentPageIndex(maxPageIndex()) }">' +
                            'Last' +
                            '</a>' +
                        '</span>' +
                    '</div>' +
                '</div>' +
            '</script>'
        );
    });
});