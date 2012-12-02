define(['ko', 'uberlearner/js/utils/dom', 'uberlearner/js/filestorage/uberphoto/list/models'], function(ko, domUtils, Models) {
    var viewModelFactory = function() {
        // PRIVATE SECTION
        /**
         * The ELLIPSES_PAGE is a dummy page that does not actually lead to images being displayed. It is merely for
         * the purpose of filling in gaps in the pagination buttons.
         * @type {Models.Page}
         */
        var ELLIPSES_PAGE = new Models.page([], '...', function(){}, false, false);
        var EMPTY_PAGE = new Models.page([], '', function(){}, false, false);
        var imageUrls = ko.observableArray([]); //this will be auto-populated by the url-list binding
        var imageData = ko.observableArray([]); //this will contain a list of page instances
        var currentImage= ko.observable();
        var currentPage = ko.observable(EMPTY_PAGE);
        var THUMBS_PER_PAGE = 15;
        var MAX_DISPLAYED_PAGE_COUNT = 7;

        /**
         * Generic method for each of the pagination titles.
         * @param pageNumber The page model instance
         * @return {Function}
         */
        var genericPageAction = function(page) {
            currentPage().isActive(false);
            page.isActive(true);
            currentPage(page);
        };
        /**
         * Calculates which pages should be visible in the pagination bar such that the current page is always
         * centred.
         * @type {*}
         */
        var visiblePages = ko.computed(function() {
            var numberOfPages = imageData().length;
            if (numberOfPages == 0)
                return [];

            var leftPadding = Math.floor((MAX_DISPLAYED_PAGE_COUNT-1)/2);
            var leftPageIndex, rightPageIndex;
            var leftElipsesVisibility=false, rightElipsesVisibility=false;

            leftPageIndex = imageData.indexOf(currentPage()) - leftPadding;
            if (leftPageIndex < 0) {
                leftPageIndex = 0;
            } else {
                leftElipsesVisibility = true;
            }
            rightPageIndex = leftPageIndex + MAX_DISPLAYED_PAGE_COUNT - 1;
            if (rightPageIndex >= numberOfPages){
                rightPageIndex = numberOfPages-1;
                leftPageIndex = rightPageIndex - MAX_DISPLAYED_PAGE_COUNT + 1;
            } else {
                rightElipsesVisibility = true;
            }
            var _visiblePages = imageData.slice(leftPageIndex, rightPageIndex+1);
            if (leftElipsesVisibility)
                _visiblePages.unshift(ELLIPSES_PAGE);
            if (rightElipsesVisibility)
                _visiblePages.push(ELLIPSES_PAGE);
            return _visiblePages;
        });

        /**
         * When the image urls variable changes, the image data needs to be refilled.
         */
        imageUrls.subscribe(function() {
            var totalThumbs = imageUrls().length;
            var maxPageNumber = Math.ceil(totalThumbs/THUMBS_PER_PAGE);
            var currentImageUrlIdx = 0;
            imageData([]);

            for (pageNumber = 1; pageNumber <= maxPageNumber; pageNumber++) {
                var pagePhotos = [];
                for(var photoIdx = 0; photoIdx < THUMBS_PER_PAGE; photoIdx++) {
                    if (currentImageUrlIdx < totalThumbs) {
                        var currentImageUrls = imageUrls()[currentImageUrlIdx];
                        pagePhotos.push(Models.photo(currentImageUrls['thumbnail'], currentImageUrls['original']));
                        currentImageUrlIdx++;
                    } else {
                        break;
                    }
                }
                imageData.push(Models.page(pagePhotos, pageNumber, genericPageAction, false, true));
            }
            if (imageData().length) {
                genericPageAction(imageData()[0]);
                currentImage(imageData()[0].photos[0]);
            } else
                currentPage(EMPTY_PAGE);
        });

        /**
         * This is the function that gets called when a user has finalized which image he/she will be using.
         */
        var selectImage = function() {
            var urlParams = domUtils.urlParams();
            var funcNum = urlParams.CKEditorFuncNum;
            try {
                window.opener.CKEDITOR.tools.callFunction(funcNum, currentImage().originalUrl);
            } catch (e) {
                alert('Image could not be applied to the editor.');
            }
            self.close();
        };

        // PUBLIC SECTION
        return {
            imageUrls: imageUrls,
            imageData: imageData,
            currentImage: currentImage,
            selectImage: selectImage,
            visiblePages: visiblePages,
            currentPage: currentPage
        };
    };
    return viewModelFactory;
});