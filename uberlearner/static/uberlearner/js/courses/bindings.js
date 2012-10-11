define(['ko', 'jquery', 'jquery-ui'], function(ko, $) {
    ko.bindingHandlers.courseResourceUri = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var value = valueAccessor();
            if (typeof(value['attrName']) == "undefined")
                value['attrName'] = 'url'
            if (typeof(value['url']) == "undefined")
            throw {
                name: 'IllegalArgumentException',
                message: 'The value of the courseResourceUri binding should contain a url'
            }
            viewModel[value.attrName](value.url);
        }
    };

    ko.bindingHandlers.uberSortableList = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            $(element).sortable({
                update: function(event, ui) {
                    // regardless of which item was moved where, we can just iterate through the
                    // items in the list and update their _order attribute.
                    var listItems = $(element).children();
                    for (var index = 0; index < listItems.length; index++) {
                        var page = ko.dataFor(listItems[index]);
                        page._order = index;
                    }
                    viewModel.savePageListOrder();
                },
                containment: $(element).parent(),
                opacity: 0.7,
                handle: '.sortable-helper-icon'
            });
        }
    };

    /**
     * This binding changes visibility of elements with a slide effect.
     * @type {Object}
     */
    ko.bindingHandlers.slideVisible = {
        init: function(element, valueAccessor) {
            // Initially set the element to be instantly visible/hidden depending on the value
            var value = valueAccessor();
            $(element).toggle(ko.utils.unwrapObservable(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
        },
        update: function(element, valueAccessor) {
            // Whenever the value subsequently changes, slowly fade the element in or out
            var value = ko.utils.unwrapObservable(valueAccessor());
            if (value)
                $(element).slideDown();
            else
                $(element).slideUp();
        }
    };
});