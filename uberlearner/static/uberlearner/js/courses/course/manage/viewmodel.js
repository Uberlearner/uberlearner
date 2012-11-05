define(['ko', 'uberlearner/js/courses/models', 'uberlearner/js/courses/bindings'], function(ko, Models) {
    var ManageCourseViewModel = function() {
        var self = this;
        var editorHasLoaded = false; //this is just an internal flag
        self.course = ko.observable(new Models.Course({}));
        self._url = ko.observable();
        self.url = ko.computed({
            read: self._url,
            write: function(value) {
                self._url(value);
                self.refreshCourseData();
            }
        });
        self._currentPageIdx = ko.observable(-1);
        self.currentPageIdx = ko.computed({
            read: self._currentPageIdx,
            write: function(value) {
                // save the current page first
                if (self.currentPage())
                    self.currentPage().save();

                self._currentPageIdx(value);

                //refresh the data for the newly selected page
                if (value >= 0 && value < self.course().pages().length) {
                    var page = self.course().pages()[value];
                    if (page.resourceUri) {
                        $.getJSON(page.resourceUri, function(data) {
                            data.course = self.course();
                            self.course().pages()[value].populate(data);
                        });
                    }
                }
            }
        });
        self.currentPage = ko.computed({
            read: function() {
                if (self.currentPageIdx() == -1)
                    return null;
                else
                    return self.course().pages()[self.currentPageIdx()];
            },
            write: function(value) {
                var newIdx = -1;
                var pages = self.course().pages();
                for (var i = 0; i < pages.length; i++) {
                    if (pages[i] == value)
                        newIdx = i;
                }
                self.currentPageIdx(newIdx);
            }
        });
        self.currentHtml = ko.computed({
            read: function() {
                if (self.currentPage())
                    return self.currentPage().html();
                else
                    return '';
            },
            write: function(value) {
                var _currentPage = self.currentPage();
                _currentPage.html(value);
                _currentPage.inSync(false);
            }
        });
        self.isActivePage = function(page) {
            var _currentPage = self.currentPage();
            if (_currentPage)
                return page.id == _currentPage.id && page.order == _currentPage.order;
            else
                return false;
        }
        self.newPageTitle = ko.observable('');

        /**
         * Listener for the create new page button at the bottom of the page list.
         */
        self.createNewPage = function() {
            var newPage = new Models.Page({});
            newPage.course = self.course();
            newPage._order = self.course().pages().length;
            newPage.title(self.newPageTitle());
            self.newPageTitle('');
            newPage.html('');
            newPage.inSync(false);
            self.course().pages.push(newPage);
            self.currentPageIdx(self.course().pages().length - 1);
        };

        /**
         * This is the page that has been marked for deletion. The actual deletion will be done by
         * a subscribed method.
         * @type {Page}
         */
        self.doomedPage = ko.observable();
        self.doomedPage.subscribe(function(page) {
            if (typeof page !== 'undefined') {
                var currentPage = self.currentPage();
                if (currentPage) {
                    //no point saving what is going to be deleted
                    if (currentPage != page)
                        currentPage.save();
                    //decrement the current page index if the deleted page is not above the current page in list order
                    if (page._order <= currentPage._order)
                        self.currentPageIdx(self.currentPageIdx()-1);
                }

                var modal = $('#page-delete-warning-modal');
                modal.modal('show');
            }
        });

        self.ckeditorOptions = {
            customConfig: '/static/uberlearner/js/main/ckeditorCustomConfig.js'
        };

        self.ckeditorOnInit = function() {
            editorHasLoaded = true;

            //this part will only be useful if the _course.pages() load before the wysiwyg instance
            if (self.course().pages().length > 0) {
                self.currentPageIdx(0);
            }
        };

        /**
         * When the user shuffles the order of the pages around, the page list order gets
         * saved to the server using this method.
         */
        self.savePageListOrder = function() {
            var data = ko.toJSON({
                objects: $.map(self.course().pages(), function(page){
                    return {
                        'id': page.id,
                        '_order': page._order,
                        'resourceUri': page.resourceUri
                    }
                })
            });
            $.ajax({
                url: self.course().pageListUri,
                type: 'PATCH',
                data: data,
                contentType: 'application/json',
                dataType: 'json',
                processData: false,
                success: function(data, textStatus, jqXHR) {
                    console.log("success data: " + data);
                    console.log("success textStatus: " + textStatus);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log("error textStatus: " + textStatus);
                    console.log("error thrown: " + errorThrown);
                    console.log("response text: " + jqXHR.responseText);
                }
            })
        };
        self.refreshCourseData = function() {
            if (self.url()) {
                $.getJSON(self.url(), function(course) {
                    var _course = new Models.Course(course);
                    self.course(_course);
                    /*
                    It is uncertain whether the editor or the course models load first. This part below takes care of the
                    case when the model loads after the editor.
                     */
                    if (_course.pages().length > 0 && editorHasLoaded) {
                        self.currentPageIdx(0);
                    }
                });
            }
        };

        self.isPreviewModeOn = ko.observable(false);
        /**
         * This method gets called by the preview function in the ui that should cause the
         * span with id "page-edit" and "page-preview" to swap visibilities.
         */
        self.togglePreviewMode = function() {
            self.isPreviewModeOn(!self.isPreviewModeOn());
        };

        /**
         * This is the method that gets called when the back button on the page itself is clicked.
         * TODO: add this method as a listener for the "real" back button when Davis.js is used.
         */
        self.goBack = function() {
            var currentPage = self.currentPage();
            if (currentPage) {
                currentPage.save();
            }
            window.location.href = self.backUrl();
        };
    };
    return ManageCourseViewModel;
});