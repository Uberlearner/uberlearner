define([
    'ko',
    'jquery',
    'uberlearner/js/utils/messages/model',
    'uberlearner/js/utils/messages/initial-messages-binding'
], function(ko, $, messageModel) {
    var viewModel = function() {
        var messages = ko.observableArray([]);
        var addMessage = function(level, message) {
            messages.push(messageModel({
                level: level,
                message: message
            }));
        };
        var levels = ['info', 'debug', 'warning', 'error', 'success'];
        var envelopeFunctions = {};
        $(levels).each(function(index, level) {
            envelopeFunctions[level] = function(message) {
                return addMessage(level, message);
            };
        });
        return $.extend({
            messages: messages,
            addMessage: addMessage
        }, envelopeFunctions);
    }();
    ko.applyBindings(viewModel, $('#message-list')[0]);
    return viewModel;
});