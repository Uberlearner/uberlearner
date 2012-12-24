define(['jquery', 'ko', 'isotope'], function($, ko, isotope) {
    var koIsotope = {
        generateIsotopeManager: function(config) {
            var url = config.url;
            var urlData = config.urlData;

            /* Helper methods and variables */
            var userProvidedMethodMissing = function() {
                throw {
                    name: 'User Provided Method Missing',
                    message: 'The user is yet to provide an implementation for this method',
                    toString: function() {
                        return this.name;
                    }
                }
            };

            /* Default Methods that the user has to over-ride */
            var onDataReceived = config.onDataReceived || userProvidedMethodMissing;
            var onDataReceivedError = config.onDataReceivedError || function(jqXHR, textStatus, errorThrown) {
                console.log("response text: " + jqXHR.responseText);
                console.log("textStatus: " + textStatus);
                console.log("error: " + errorThrown);
            };

            /* Observable Subscriptions */
            url.subscribe(function(newUrl) {
                if (typeof(newUrl) === 'undefined' || newUrl == '')
                    return; //don't bother with the ajax call if the url is not valid

                $.ajax({
                    url: newUrl,
                    data: urlData(), //this method has to be supplied by the user in the binding
                    success: onDataReceived, //this method has to be supplied by the user in the binding
                    error: onDataReceivedError //this method has to be supplied by the user in the binding
                });
            });

            /* Other initialization chores */
            //templates
            var itemTemplate = config.itemTemplate;
            $(function() {
                $('body').append($(itemTemplate));
            });

            /* Return publicly accessible attributes. */
            return {
                url: url,
                urlData: urlData,
                onDataReceived: onDataReceived,
                onDataReceivedError: onDataReceivedError,
                config: config
            }
        }
    };

    //The bindings - These don't need to be returned by the module
    ko.bindingHandlers.isotope = function() {
        /**
         * Used to update an attribute of a given object. If the attribute doesn't exist, then
         * it is inserted into the object as on observable. If the attribute exists then it is
         * merely updated.
         * Note that this method is aware of knockout observables. This means that if the attribute
         * exists already in the object, and is an observable, it will not be replaced by something
         * that is not an observable.
         * @param obj The object of concern
         * @param attr The attribute of the object that has to be replaced
         * @param val The desired value of that attribute of the object
         */
        var updateAttribute = function(obj, attr, val) {
            if (typeof(obj[attr]) === 'undefined') {
                obj[attr] = ko.observable(val);
            } else if (ko.isObservable(obj[attr])) {
                obj[attr](val);
            } else {
                obj[attr] = val;
            }
        };

        var templateEngine = new ko.nativeTemplateEngine();

        var init = function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var options = ko.utils.unwrapObservable(valueAccessor());
            if (typeof(options['url']) !== 'undefined') {
                updateAttribute(viewModel, 'url', options['url']);
            }

            //empty the element and start anew
            while(element.firstChild)
                ko.removeNode(element.firstChild);

            //apply the template to the element
            ko.renderTemplate(viewModel.isotopeManager.config.itemTemplate, viewModel, { templateEngine: templateEngine }, element, 'replaceChildren');

            $(element).isotope();

            return {'controlsDescendantBindings': true};
        };

        var update = function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {

        };

        return {
            init: init,
            update: update
        };
    }();

    return koIsotope;
});