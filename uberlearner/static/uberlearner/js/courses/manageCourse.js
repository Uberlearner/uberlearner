$(function() {
    ko.bindingHandlers.courseResourceUri = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var value = valueAccessor(), allBindings = allBindingsAccessor();
            viewModel.url(value);
        }
    };

    function Page(data) {
        var self = this;
        self.slug = ko.observable();
        self.title = ko.observable();
        self.html = ko.observable();
        /**
         * When the model is syncing with the server, it needs to keep the user involved. Some parameters in the
         * UI need to be changed to show the user what is going on. The saving attribute is used by some UI elements.
         * This should be made true when an ajax request is sent and false when the response is received.
         *
         * Later on, if there are multiple ajax requests being processed, this could be converted to a number that is
         * incremented when the request is sent and decremented when the response is received.
         * @type {Boolean}
         */
        self.saving = ko.observable(false);

        /**
         * Indicates whether the model is in sync with the server.
         * @type {Boolean}
         */
        self.inSync = ko.observable(false);

        self.saveButtonText = ko.computed(function() {
            if (self.saving())
                return "Saving...";
            else if (self.inSync())
                return "Saved";
            else
                return "Save";
        });

        self.isSaveButtonDisabled = ko.computed(function() {
            if (self.saving() || self.inSync())
                return true;
            return false;
        });

        self.title.subscribe(function(newValue) {
            self.inSync(false);
        });

        self.populate = function(data) {
            self.id = data.id || -1;
            self.course = data.course || null;
            self._order = data._order;
            self.creationTimestamp = data.creationTimestamp;
            self.lastModified = data.lastModified;
            self.popularity = data.popularity;
            self.resourceUri = data.resourceUri;
            self.slug(data.slug);
            self.title(data.title);
            self.html(data.html);
        };

        self.populate(data);

        /**
         * The model might contain a lot of things besides the model information. This information should not be
         * sent to the server during ajax requests. This method filters out the attributes that are useful for ajax.
         * In addition, some extra attributes (like course_id) may have to be added to ensure integrity of data.
         * @private
         */
        self.getAjaxData = function() {
            return {
                id: self.id == -1 ? undefined : self.id,
                course_id: self.course.id,
                _order: self._order,
                //creationTimestamp: self.creationTimestamp,
                //lastModified: self.lastModified,
                popularity: self.popularity,
                resourceUri: self.resourceUri,
                slug: self.slug(),
                title: self.title(),
                html: self.html()
            };
        }
        self.save = function() {
            var uri, method;
            if (self.resourceUri && self.id != -1) {
                //This object has a record on the server already.
                uri = self.resourceUri;
                method = 'PUT';
            } else {
                //A new object needs to be created on the server
                uri = self.course.pageListUri;
                method = 'POST';
            }
            $.ajax({
                url: uri,
                type: method,
                data: ko.toJSON(self.getAjaxData()),
                contentType: 'application/json',
                dataType: 'json',
                processData: false,
                beforeSend: function(jqXHR, settings) {
                    self.saving(true);
                },
                complete: function(jqXHR, textStatus) {
                    self.saving(false);
                },
                success: function(data, textStatus, jqXHR) {
                    if (data.resourceUri)
                        self.resourceUri = data.resourceUri;
                    if (data.id)
                        self.id = data.id;
                    self.inSync(true);
                    console.log("success data: " + data);
                    console.log("success textStatus: " + textStatus);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log("error textStatus: " + textStatus);
                    console.log("error thrown: " + errorThrown);
                    console.log("response text: " + jqXHR.responseText);
                }
            });
        };

        self.delete = function() {
            if (self.resourceUri) {
                // only if the object exists on the server does this request get made
                $.ajax({
                    type: 'DELETE',
                    url: self.resourceUri,
                    data: ko.toJSON(self.getAjaxData()),
                    contentType: 'application/json',
                    dataType: 'json',
                    processData: false,
                    success: function() {
                        console.log("'" + self.title() + "' page deleted successfully");
                        $('#page-delete-warning-modal').modal('hide');
                        //TODO: check if the memory is cleared for this page. Not sure how garbage collection works in browsers.
                        self.course.pages.remove(self);
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log("error textStatus: " + textStatus);
                        console.log("error thrown: " + errorThrown);
                        console.log("response text: " + jqXHR.responseText);
                    }
                });
            }
        };
    }

    function Instructor(data) {
        if (typeof(data) == 'undefined') {
            data = {};
        }
        this.absoluteUrl = data.absoluteUrl;
        this.firstName = data.firstName;
        this.lastName = data.lastName;
        this.lastLogin = data.lastLogin;
        this.resourceUri = data.resourceUri;
        this.username = data.username;
    }

    function Course(data) {
        var self = this;
        self.absoluteUrl = data.absoluteUrl;
        self.creationTimestamp = data.creationTimestamp;
        self.description = data.description;
        self.id = data.id;
        self.instructor = new Instructor(data.instructor);
        self.isPublic = data.isPublic;
        self.lastModified = data.lastModified;
        self.pageListUri = data.pageListUri;
        self.pages = ko.observableArray($.map((data.pages || []), function(page, index) {
            page.course = self;
            var createdPage = new Page(page);
            createdPage.inSync(true);
            return createdPage;
        }));
        self.popularity = data.popularity;
        self.resourceUri = data.resourceUri;
        self.slug = data.slug;
        self.title = data.title;
    }

    var ManageCourseViewModel = function() {
        var self = this;
        self.course = ko.observable(new Course({}));
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
            var newPage = new Page({});
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

        self.tinymceOptions = {
            theme_advanced_resizing: true
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
                    var _course = new Course(course);
                    self.course(_course);
                    if (_course.pages().length > 0) {
                        //TODO: find a tinymce ready event to attach the following command to.
                        //self.currentPageIdx(0);
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
    };

    ko.bindingHandlers.uberSortableList = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            $(element).sortable({
                update: function(event, ui) {
                    // regardless of which item was moved where, we can just iterate through the
                    // items in the list and update their _order attribute.
                    var listItems = $(element).children();
                    for (var index = 0; index < listItems.length; index++) {
                        var page = ko.dataFor(listItems[index]);
                        page._order = index;
                    }
                    viewModel.savePageListOrder();
                },
                containment: $(element).parent(),
                opacity: 0.7,
                handle: '.sortable-helper-icon'
            });
        }
    };

    /**
     * This binding changes visibility of elements with a slide effect.
     * @type {Object}
     */
    ko.bindingHandlers.slideVisible = {
        init: function(element, valueAccessor) {
            // Initially set the element to be instantly visible/hidden depending on the value
            var value = valueAccessor();
            $(element).toggle(ko.utils.unwrapObservable(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
        },
        update: function(element, valueAccessor) {
            // Whenever the value subsequently changes, slowly fade the element in or out
            var value = ko.utils.unwrapObservable(valueAccessor());
            if (value)
                $(element).slideDown();
            else
                $(element).slideUp();
        }
    };
    ko.applyBindings(new ManageCourseViewModel(), $('#course-management-block')[0]);
});
