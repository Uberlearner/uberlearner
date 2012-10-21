define(['ko', 'uberlearner/js/courses/models', 'uberlearner/js/utils/bindings/url-list'], function(ko, Models) {
    var viewModelFactory = function() {
        // PRIVATE SECTION
        var course = ko.observable(new Models.Course({}));
        /**
         * All the pages of the course are stored in the course model. This is merely the index that holds the current
         * page. A value of -1 implies that the current index hasn't been set.
         * @type {*}
         */
        var currentPageIdx = ko.observable(-1);
        var currentPage = ko.observable(new Models.Page({}));
        var courseResourceUri = ko.observable();
        var pageResourceUri = ko.observable();
        var currentPageContent = ko.computed(function() {
            //The html variable used here is a hack. This is because the ko.computed tracks its dependencies at runtime
            //depending on what was called. This means that unless currentPage().html() is not called in all paths of
            //the function, it might not show up as a dependency and hence not get triggered when the html of the current
            //page gets updated in the populate method.
            //TODO: find if this hack can be avoided by manually causing the re-computation of this function
            var html = currentPage().html();
            if (currentPage().id == -1) {
                return "No pages were found in this course!"; //TODO: fetch an html template from the server
            } else {
                return html;
            }
        });

        /**
         * This function uses the pageResourceUri and the course model to find the index of the current page in the
         * course.pages array and to update it in the currentPageIdx variable.
         */
        function updateCurrentPageIdx() {
            //if currentPage isn't valid then the answer is -1
            //if course doesn't contain any pages then the answer is -1
            if (currentPage().id == -1 || course().pages().length == 0) {
                currentPageIdx(-1);
                return;
            }

            var pages = course().pages();
            for (pageIdx in pages) {
                if (pages[pageIdx].id == currentPage().id) {
                    currentPageIdx(pageIdx);
                    return; //no need to continue if the page was found
                }
            }
            //this means that we have a page that doesn't exist in the course().pages() array
            throw new Error("currentPage doesn't correspond to any of the pgaes in course.pages");
        };

        /**
         * When the courseResourceUri gets updated, get the data at that endpoint and populate the local variables.
         */
        courseResourceUri.subscribe(function(newValue) {
            if(newValue) {
                $.getJSON(newValue, function(obj) {
                    course(new Models.Course(obj));
                    updateCurrentPageIdx(); //might not succeed if pageResourceUri hasn't been loaded but that's ok
                    if (currentPageIdx() != -1 && currentPage().id != -1)
                        course().pages()[currentPageIdx()].html(currentPage().html())
                });
            }
        });

        /**
         * When the pageResourceUri gets updated, get the data at the endpoint and populate the local variables.
         * Since the order in which subscriptions get called is not determined, this function does not assume that
         * the course model exists.
         */
        pageResourceUri.subscribe(function(newValue) {
            if (newValue) {
                $.getJSON(newValue, function(obj) {
                    currentPage().populate(obj);
                    updateCurrentPageIdx(); // might not succeed if courseResourceUri hasn't been loaded but that's ok
                    if (currentPageIdx() != -1) {
                        course().pages()[currentPageIdx()].html(obj.html || '');
                    }
                });
            }
        });

        // RETURN PUBLIC OBJECT
        return {
            courseResourceUri: courseResourceUri,
            pageResourceUri: pageResourceUri,
            currentPageContent: currentPageContent
        };
    };
    return viewModelFactory;
});