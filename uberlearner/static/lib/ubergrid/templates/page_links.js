define(['jquery'], function() {
    $(function() {
        if ($('#ko_uberGrid_pageLinks').length == 0) {
            $('body').append(
                '<script type="text/html" id="ko_uberGrid_pageLinks">' +
                    '<div class="row" data-bind="visible: dataExists() && maxPageIndex() > 0">' +
                    '<div class="pagination pagination-centered">' +
                    '<ul>'+
                    '<li data-bind="css: {disabled:!hasPrevious()}, click: function(){currentPageIndex(0)}">' +
                    '<a href="#">First</a>' +
                    '</li>' +
                    '<li data-bind="css: {disabled:!hasPrevious()}, click: function(){currentPageIndex(currentPageIndex()-1)}">' +
                    '<a href="#">Previous</a>' +
                    '</li>' +
                    '<span data-bind="foreach: pageIndexes">' +
                    '<li data-bind="css: {active: $data == $root.currentPageIndex() }, click: function(){$root.currentPageIndex($data)}">' +
                    '<a data-bind="text: $data + 1"></a>' +
                    '</li>' +
                    '</span>' +
                    '<li data-bind="css: {disabled:!hasNext()}, click: function(){currentPageIndex(currentPageIndex()+1)}">' +
                    '<a href="#">Next</a>' +
                    '</li>' +
                    '<li data-bind="css: {disabled:!hasNext()}, click: function(){currentPageIndex(maxPageIndex())}">' +
                    '<a href="#">Last</a>' +
                    '</li>' +
                    '</ul>'+
                    '</div>' +
                '</script>'
            );
        }
    });
});