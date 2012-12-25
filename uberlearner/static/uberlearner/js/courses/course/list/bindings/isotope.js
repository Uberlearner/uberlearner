define(['jquery', 'ko', 'isotope'], function($, ko) {
    ko.bindingHandlers.isotope = {
        /*
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var options = ko.utils.unwrapObservable(valueAccessor());
            var itemSelector = options.itemSelector || '.item';
            var layoutMode = options.layoutMode || 'masonry';
            $(element).isotope({
                itemSelector: itemSelector,
                layoutMode: layoutMode
            });
        },
        */
        update: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var options = ko.utils.unwrapObservable(valueAccessor());
            if (options) {
                if (Object.prototype.toString.call(options) === '[object Array]') {
                    $.fn.isotope.apply($(element), options);
                } else {
                    $(element).isotope(options);
                }
            }
        }
    };
});