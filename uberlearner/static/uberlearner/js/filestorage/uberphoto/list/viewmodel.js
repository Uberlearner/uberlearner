define(['ko', 'uberlearner/js/utils/dom'], function(ko, domUtils) {
    var pageName = function(title, action, isActive, isEnabled) {
        return {
            title: title,
            action: action,
            isActive: ko.observable(isActive),
            isEnabled: isEnabled
        }
    };

    var viewModelFactory = function() {
        // PRIVATE SECTION
        var imageData = ko.observableArray([]); //this will be auto-populated by the url-list binding
        var currentImage= ko.observable();
        var THUMBS_PER_PAGE = 15;
        var MAX_PAGE_TITLES = 7;
        /**
         * A one-indexed number corresponding to the current page being displayed.
         * @type {*}
         */
        var currentPageNumber = ko.observable(1);

        /**
         * A list of images corresponding to the current page.
         * @type {*}
         */
        var currentPageImages = ko.computed(function() {
            var totalThumbs = imageData().length;
            var maxPageNumber = Math.ceil(totalThumbs/THUMBS_PER_PAGE);

            if(totalThumbs == 0)
                return [];
            if (currentPageNumber() < 1 || currentPageNumber() > maxPageNumber)
                throw {
                    name: 'ValueError',
                    message: 'The current page number is not within acceptable bounds'
                }

            var startingIndex = (currentPageNumber()-1) * THUMBS_PER_PAGE;
            var endingIndex = startingIndex + THUMBS_PER_PAGE;
            if (endingIndex > totalThumbs)
                endingIndex = undefined;

            return imageData.slice(startingIndex, endingIndex);
        });

        /**
         * The entirety of the page names regardless of whether or not they can actually be seen by the user.
         * @type {*}
         */
        var pageNames = ko.observableArray([]);
        /**
         * Generates methods for each of the pagination titles.
         * @param pageNumber The page number of the title.
         * @return {Function}
         */
        var pageActionGenerator = function(pageNumber) {
            return function() {
                var oldPageNumber = currentPageNumber();
                pageNames()[oldPageNumber-1].isActive(false);
                currentPageNumber(pageNumber);
                pageNames()[pageNumber-1].isActive(true);
            };
        }
        /**
         * Calculates which pages should be visible in the pagination bar such that the current page is always
         * centred.
         * @type {*}
         */
        var visiblePageNames = ko.computed(function() {
            var numberOfPages = Math.ceil(imageData().length/THUMBS_PER_PAGE);
            if (numberOfPages == 0)
                return [];

            var leftPadding = Math.floor((MAX_PAGE_TITLES-1)/2);
            var leftPageIndex, rightPageIndex;
            var leftElipsesVisibility=false, rightElipsesVisibility=false;

            leftPageIndex = currentPageNumber() - leftPadding - 1;
            if (leftPageIndex < 0) {
                leftPageIndex = 0;
            } else {
                leftElipsesVisibility = true;
            }
            rightPageIndex = leftPageIndex + MAX_PAGE_TITLES - 1;
            if (rightPageIndex >= numberOfPages){
                rightPageIndex = numberOfPages-1;
                leftPageIndex = rightPageIndex - MAX_PAGE_TITLES + 1;
            } else {
                rightElipsesVisibility = true;
            }
            var _visiblePageNames = pageNames.slice(leftPageIndex, rightPageIndex+1);
            if (leftElipsesVisibility)
                _visiblePageNames.unshift(pageName('...', function() {}, false, false));
            if (rightElipsesVisibility)
                _visiblePageNames.push(pageName('...', function() {}, false, false));
            return _visiblePageNames;
        });

        /**
         * When the image data changes, the page names need to be updated.
         */
        imageData.subscribe(function() {
            var totalThumbs = imageData().length;
            var maxPageNumber = Math.ceil(totalThumbs/THUMBS_PER_PAGE);

            for (pageNumber = 1; pageNumber <= maxPageNumber; pageNumber++) {
                pageNames.push(pageName(pageNumber, pageActionGenerator(pageNumber), false, true));
            }
            pageNames()[currentPageNumber()-1].isActive(true);
        });

        /**
         * This is the function that gets called when a user has finalized which image he/she will be using.
         */
        var selectImage = function() {
            var urlParams = domUtils.urlParams();
            var funcNum = urlParams.CKEditorFuncNum;
            try {
                window.opener.CKEDITOR.tools.callFunction(funcNum, currentImage().original);
            } catch (e) {
                alert('Image could not be applied to the editor.');
            }
            self.close();
        };

        // PUBLIC SECTION
        return {
            imageData: imageData,
            currentPageImages: currentPageImages,
            currentImage: currentImage,
            currentPageNumber: currentPageNumber,
            selectImage: selectImage,
            visiblePageNames: visiblePageNames
        };
    };
    return viewModelFactory;
});