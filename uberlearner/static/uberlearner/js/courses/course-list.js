require(['jquery', 'ko', 'uberGrid', 'bootstrap'], function($, ko, uberGrid, bootstrap) {
    var PopularCourses = function() {
        var self = this;

        self.gridViewModel = new uberGrid.viewModel({
            pageSize: 5,
            columns: [
                { headerText: "Title", field: "title", link: "absoluteUrl" },
                { headerText: "Instructor", field: function(row) {
                    return row.instructor.username;
                }, link: function(row) {
                    return row.instructor.absoluteUrl;
                }
                },
                { headerText: "Created on", field: 'creationTimestamp' },
                { headerText: "Popularity", field: 'popularity' }
            ],
            defaultText: 'We don\'t have any courses to offer yet. Check again in a few days!',
            maxPageCount: 9
        });
    };

    var NewCourses = function() {
        var self = this;

        self.gridViewModel = new uberGrid.viewModel({
            pageSize: 5,
            columns: [
                { headerText: "Title", field: "title", link: "absoluteUrl" },
                { headerText: "Instructor", field: function(row) {
                    return row.instructor.username;
                }, link: function(row) {
                    return row.instructor.absoluteUrl;
                }
                },
                { headerText: "Created on", field: 'creationTimestamp' },
                { headerText: "Popularity", field: 'popularity' }
            ],
            defaultText: 'We don\'t have any courses to offer yet. Check again in a few days!',
            maxPageCount: 9
        });
    };
    $(function(){
        ko.applyBindings(new PopularCourses(), $("#popular-course-list")[0]);
        ko.applyBindings(new NewCourses(), $("#new-course-list")[0]);
    });
});

