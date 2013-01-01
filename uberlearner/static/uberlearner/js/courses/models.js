define(['ko'], function(ko) {
    var Models = {};
    Models.Page = function (data) {
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
         *
         * TODO: take this out of the model. Events for pre-save and post-save are to be put in its place.
         *
         * @type {Boolean}
         */
        self.saving = ko.observable(false);

        /**
         * Indicates whether the model is in sync with the server.
         * @type {Boolean}
         */
        self.inSync = ko.observable(false);

        //TODO: take this out of here. It doesn't belong to the model
        self.saveButtonText = ko.computed(function() {
            if (self.saving())
                return "Saving...";
            else if (self.inSync())
                return "Saved";
            else
                return "Save";
        });

        //TODO: the ui stuff doesn't belong in the model. take it out.
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

    Models.Instructor = function(data) {
        if (typeof(data) == 'undefined') {
            data = {};
        }
        this.absoluteUrl = data.absoluteUrl;
        this.firstName = data.firstName;
        this.lastName = data.lastName;
        this.lastLogin = data.lastLogin;
        this.resourceUri = data.resourceUri;
        this.username = data.username;

        this.getFullName = function() {
            if (!this.firstName && !this.lastName){
                return "Anonymous";
            } else {
                return this.firstName + ' ' + this.lastName;
            }
        };
    }

    Models.Course = function (data) {
        var self = this;
        data = data || {};
        self.absoluteUrl = data.absoluteUrl;
        self.creationTimestamp = data.creationTimestamp;
        self.description = data.description;
        self.id = data.id;
        self.instructor = new Models.Instructor(data.instructor);
        self.isPublic = ko.observable(data.isPublic);
        self.lastModified = data.lastModified;
        self.pageListUri = data.pageListUri;
        self.pages = ko.observableArray($.map((data.pages || []), function(page, index) {
            page.course = self;
            var createdPage = new Models.Page(page);
            createdPage.inSync(true);
            return createdPage;
        }));
        self.popularity = data.popularity;
        self.resourceUri = data.resourceUri;
        self.slug = data.slug;
        self.title = data.title;
        self.photo = data.photo;
        self.thumbnail = data.thumbnail || '';
        self.creationTimePrecise = data.creationTimePrecise || '';
        self.enrolled = data.enrolled || false;

        self.truncatedDescription = function(length) {
            if (self.description.length > length) {
                return self.description.substring(0, length) + '...';
            } else {
                return self.description;
            }
        }
    }

    return Models;
});