define(['ko', 'uberlearner/js/courses/models', 'uberGrid', 'uberlearner/js/utils/bindings/url-list'], function(ko, Models, uberGrid) {
    var CourseDetailModelView = function() {
        var self = this;
        self.isEnrolled = ko.observable(false);
        self.courseUrl = ko.observable();
        self.enrollmentUrl = ko.observable();
        self.postEnrollmentUrl = ko.observable();
        self.course = ko.observable(new Models.Course());

        self.paginationViewModel = new uberGrid.viewModel({
            pageSize: 16,
            dataAdapter: function(data) {
                return new Models.Enrollment(data);
            }
        });

        /* SUBSCRIPTIONS */
        /**
         * When the enrollment url is loaded through the urlList binding, this method goes to the url and
         * finds out whether the current user is enrolled in the course or not.
         */
        self.enrollmentUrl.subscribe(function(url) {
            $.get(self.enrollmentUrl(), function(data) {
                data = (data == "True" ? true : false); //convert the string to a boolean
                self.isEnrolled(data)
            });
        });
        /**
         * When the course url is loaded through the urlList binding, this method goes to the url and
         * finds out whether the current course is public or private.
         */
        self.courseUrl.subscribe(function(url) {
            $.ajax({
                url: url,
                success: function(course) {
                    self.course(new Models.Course(course));
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log("error textStatus: " + textStatus);
                    console.log("error thrown: " + errorThrown);
                    console.log("response text: " + jqXHR.responseText);
                }
            });
        });

        /* BEHAVIOUR */
        self.toggleEnrollment = function() {
            if (!self.isEnrolled()) {
                //sending data is not required for enrollment.
                $.ajax({
                    type: 'POST',
                    url: self.enrollmentUrl(),
                    beforeSend: function(jqXHR, settings) {
                        jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val())
                    },
                    success: function() {
                        self.isEnrolled(true);
                        window.location.href = self.postEnrollmentUrl();
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log("error textStatus: " + textStatus);
                        console.log("error thrown: " + errorThrown);
                        console.log("response text: " + jqXHR.responseText);
                    }
                });
            } else {
                //TODO: figure out whether it is even necessary to have this option.
            }
        };
        self.toggleVisibility = function() {
            var isPublic = self.course().isPublic();
            var desiredVisibility = isPublic ? false : true;
            $.ajax({
                type: 'PATCH',
                url: self.courseUrl(),
                contentType: 'application/json',
                beforeSend: function(jqXHR, settings) {
                    jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val())
                },
                data: ko.toJSON({
                    'id': self.course().id,
                    'isPublic': self.course().isPublic() ? false : true,
                    'resourceUri': self.course().resourceUri
                }),
                success: function(data) {
                    self.course().isPublic(desiredVisibility);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log("error textStatus: " + textStatus);
                    console.log("error thrown: " + errorThrown);
                    console.log("response text: " + jqXHR.responseText);
                }
            });
        };
    };
    return CourseDetailModelView;
});