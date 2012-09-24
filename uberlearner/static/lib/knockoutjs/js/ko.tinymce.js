//////////////////////////////////////////////////////////////////////////
// This binding has been borrowed from
// https://github.com/SteveSanderson/knockout/wiki/Bindings---tinyMCE
// It has been modified to work with requirejs
//////////////////////////////////////////////////////////////////////////

require(['ko', 'tinymce'], function(ko, tinymce) {
    //sometimes tinymce is also used as tinyMCE
    var tinyMCE = tinymce;

    ko.bindingHandlers.tinymce = {
        init: function (element, valueAccessor, allBindingsAccessor, context) {
            var options = allBindingsAccessor().tinymceOptions || {};
            var modelValue = valueAccessor();
            var value = ko.utils.unwrapObservable(valueAccessor());
            var el = $(element);


            options.setup = function (ed) {

                ed.onChange.add(function (editor, l) { //handle edits made in the editor. Updates after an undo point is reached.
                    if (ko.isWriteableObservable(modelValue)) {
                        modelValue(l.content);
                    }
                });

                ed.onInit.add(function (ed, evt) { // Make sure observable is updated when leaving editor.
                    var dom = ed.dom;
                    var doc = ed.getDoc();
                    tinymce.dom.Event.add(doc, 'blur', function (e) {
                        if (ko.isWriteableObservable(modelValue)) {
                            modelValue(ed.getContent({ format: 'raw' }));
                        }
                    });
                });

            };

            //handle destroying an editor (based on what jQuery plugin does)
            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                $(element).parent().find("span.mceEditor,div.mceEditor").each(function (i, node) {
                    var ed = tinyMCE.get(node.id.replace(/_parent$/, ""));
                    if (ed) {
                        ed.remove();
                    }
                });
            });

            //$(element).tinymce(options);
            setTimeout(function () { $(element).tinymce(options); }, 0);
            el.val(value);

        },
        update: function (element, valueAccessor, allBindingsAccessor, context) {
            var el = $(element);
            var value = ko.utils.unwrapObservable(valueAccessor());
            var id = el.attr('id');

            //handle programmatic updates to the observable
            // also makes sure it doesn't update it if it's the same.
            // otherwise, it will reload the instance, causing the cursor to jump.
            if (id !== undefined && id !== '') {
                var content = tinyMCE.getInstanceById(id).getContent({ format: 'raw' });
                if (content !== value) {
                    el.val(value);
                }
            }
        }
    };
});
