define(['ko'], function(ko) {
    var Models = {};

    Models.photo = function(thumbnailUrl, originalUrl) {
        return {
            thumbnailUrl: thumbnailUrl,
            originalUrl: originalUrl,
            toString: function() {
                return originalUrl;
            }
        };
    };

    Models.page = function(photos, title, action, isActive, isEnabled) {
        var _isActive = ko.observable(isActive);
        var _isEnabled = ko.observable(isEnabled);
        return {
            title: title,
            action: action,
            isActive: _isActive,
            isEnabled: _isEnabled,
            photos: photos,
            toString: function() {
                return "Title: " + title + " photos: [" + photos + "]";
            }
        }
    };

    return Models;
});
