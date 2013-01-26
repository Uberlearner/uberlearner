require([
    'jquery', 'ko', 'uberGrid', 'bootstrap', 'uberlearner/js/courses/models', 'uberlearner/js/utils/messages/viewmodel'
], function($, ko, uberGrid, bootstrap, courseModels) {
    var InstructorCoursesPagedGridModel = function() {
        var self = this;

        self.gridViewModel = new uberGrid.viewModel({
            pageSize: 9,
            sortingOptions: [
                { name: 'Title', field: 'title'},
                { name: 'Oldest first', field: 'creation_timestamp'},
                { name: 'Newest first', field: '-creation_timestamp'},
                { name: 'Popularity', field: '-popularity'}
            ],
            defaultSortingOptionIndex: 3,
            defaultText: 'No courses taught by this instructor could be found!',
            maxPageCount: 9,
            dataAdapter: function(data) {
                return new courseModels.Course(data);
            }
        });
    };

    var StudentEnrollmentsPagedGridModel = function() {
        var self = this;

        self.gridViewModel = new uberGrid.viewModel({
            pageSize: 9,
            sortingOptions: [
                { name: 'Title', field: 'course__title'},
                { name: 'Oldest first', field: 'course__creation_timestamp'},
                { name: 'Newest first', field: '-course__creation_timestamp'},
                { name: 'Popularity', field: '-course__popularity'}
            ],
            defaultSortingOptionIndex: 3,
            defaultText: 'This user is not enrolled in any courses',
            maxPageCount: 9,
            dataAdapter: function(data) {
                return new courseModels.Enrollment(data);
            }
        });
    };

    $(function() {
        var instructorCourseList = $('#instructor-course-list')[0];
        var studentCourseEnrolledList = $('#student-course-enrolled-list')[0];

        if (instructorCourseList) {
            ko.applyBindings(new InstructorCoursesPagedGridModel(), instructorCourseList);
        }
        if (studentCourseEnrolledList) {
            ko.applyBindings(new StudentEnrollmentsPagedGridModel(), studentCourseEnrolledList);
        }
    });
});