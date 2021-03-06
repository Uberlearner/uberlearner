/**
 * This contains all the utility functions that deal with DOM manipulation.
 */

define([], function() {
    return function() {
        /**
         * Gets the GET parameters in the url in the form of an Javascript object.
         * @return {*} A javascript object containing the GET parameters in the url of the page
         */
        var urlParams = function() {
            return decodeURIComponent(window.location.search.slice(1))
                .split('&')
                .reduce(function (returnObj, str) {
                    var keyVal = str.split('=');
                    returnObj[keyVal[0]] = keyVal[1];
                    return returnObj;
                }, {});
        };

        return {
            urlParams: urlParams
        }
    }();
});