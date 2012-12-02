//////////////////////////////////////////////////////////////////////////////////
// This binding has been heavily influenced by the Stack Overflow post:
// http://stackoverflow.com/questions/10713155/knockout-ckeditor-single-page-app
// which has been itself heavily influenced by:
// https://github.com/SteveSanderson/knockout/wiki/Bindings---tinyMCE
//////////////////////////////////////////////////////////////////////////////////

require(['ko', 'jquery', 'ckeditor', 'jquery_ckeditor'], function(ko, $, ckeditor) {
    ko.bindingHandlers.ckeditor = {
        init: function (element, valueAccessor, allBindingsAccessor, context) {
            var options = allBindingsAccessor().ckeditorOptions || {};
            var onInit = allBindingsAccessor().ckeditorOnInit;

            var modelValue = valueAccessor();
            var value = ko.utils.unwrapObservable(modelValue);

            //init ckeditor
            $(element).html(value);
            $(element).ckeditor(onInit, options);

            var editor = $(element).ckeditorGet();

            //handle edits made in the editor
            editor.on('blur', function (e) {
                var self = this;
                if (ko.isWriteableObservable(self)) {
                    self($(e.listenerData).val());
                }
            }, modelValue, element);


            //handle destroying an editor (based on what jQuery plugin does)
            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                //var existingEditor = CKEDITOR.instances[element.name];
                var existingEditor = $(element).ckeditorGet();
                existingEditor.destroy(true);
            });
        },
        update: function (element, valueAccessor, allBindingsAccessor, context) {
            //handle programmatic updates to the observable
            var value = ko.utils.unwrapObservable(valueAccessor());
            $(element).val(value);
        }
    };
});