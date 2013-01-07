define(['ko'], function(ko) {
    /**
     * This knockout binding can be used to get arbitrary data from the server during page-rendering.
     * Even though there are many other mechanisms of achieving this task, this one will be used as it
     * automatically populates the viewmodel in question with the given data. The value of this binding
     * has to be a map/dictionary. The keys of this dictionary are the variables that will be written to
     * in this binding. If those variables don't exist, then observables will be created. If they do exist
     * and are observables, their value will be changed appropriately. If the said keys do exist in the
     * viewmodel but are not observables, then they will be assigned the appropriate value.
     * @type {Object}
     */
    ko.bindingHandlers.data = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var dict = ko.utils.unwrapObservable(valueAccessor());
            for (var key in dict) {
                var value = dict[key];
                if (typeof(viewModel[key]) !== 'undefined') {
                    if (ko.isObservable(viewModel[key]))
                        viewModel[key](value);
                    else
                        viewModel[key] = value;
                } else {
                    viewModel[key] = ko.observable(value);
                }
            }
        }
    };
});