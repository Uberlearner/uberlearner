define(['ko', 'uberlearner/js/courses/models', 'uberlearner/js/utils/bindings/url-list'], function(ko, Models) {
    var CourseDetailModelView = function() {
        var self = this;
        self.isEnrolled = ko.observable(false);
        self.courseUrl = ko.observable();
        self.enrollmentUrl = ko.observable();

        /* SUBSCRIPTIONS */
        self.enrollmentUrl.subscribe(function(url) {
            $.get(self.enrollmentUrl(), function(data) {
                data = (data == "True" ? true : false);
                self.isEnrolled(data)
            });
        });

        /* BEHAVIOUR */
        self.toggleEnrollment = function() {
            if (!self.isEnrolled()) {
                $.ajax({
                    type: 'POST',
                    url: self.enrollmentUrl(),
                    beforeSend: function(jqXHR, settings) {
                        jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val())
                    },
                    success: function() {
                        self.isEnrolled(true);
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log("error textStatus: " + textStatus);
                        console.log("error thrown: " + errorThrown);
                        console.log("response text: " + jqXHR.responseText);
                    }
                });
            } else {
                //The user is trying to withdraw from the course. If they do that, then the history of
                //TODO
            }
        };
    };
    return CourseDetailModelView;
});