define(['ko', 'uberlearner/js/utils/dom'], function(ko, domUtils) {
    var viewModelFactory = function() {
        // PRIVATE SECTION
        var imageData = ko.observableArray(); //this will be auto-populated by the url-list binding
        var currentImageData = ko.observable();

        /**
         * This is the function that gets called when a user has finalized which image he/she will be using.
         */
        var selectImage = function() {
            var urlParams = domUtils.urlParams();
            var funcNum = urlParams.CKEditorFuncNum;
            try {
                window.opener.CKEDITOR.tools.callFunction(funcNum, currentImageData().original);
            } catch (e) {
                alert('Image could not be applied to the editor.');
            }
            self.close();
        };

        // PUBLIC SECTION
        return {
            imageData: imageData,
            currentImageData: currentImageData,
            selectImage: selectImage
        };
    };
    return viewModelFactory;
});