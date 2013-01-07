define([], function() {
    var model = function(data) {
        var level = data.level || 'INFO';
        var message = data.message || '';
        var levelToClassMap = {
            'info': 'alert-info',
            'debug': '',
            'success': 'alert-success',
            'warning': 'alert-danger',
            'error': 'alert-error'
        };
        var getClass = function() {
            return levelToClassMap[level];
        };
        return {
            level: level,
            message: message,
            getClass: getClass
        };
    };

    return model;
});