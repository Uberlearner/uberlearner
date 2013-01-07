define(['ko', 'uberlearner/js/utils/messages/model'], function(ko, messageModel){
    ko.bindingHandlers.initialMessages = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var messages = ko.utils.unwrapObservable(valueAccessor());
            for (var messageIdx in messages) {
                var message = messages[messageIdx];
                viewModel.messages.push(messageModel(message));
            }
        }
    }
});