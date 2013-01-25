require([
    'jquery', 'ko', 'uberGrid', 'bootstrap', 'uberlearner/js/utils/messages/viewmodel'
], function($, ko, uberGrid, bootstrap) {
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
            maxPageCount: 9
        });
    };

    $(function() {
        ko.applyBindings(new InstructorCoursesPagedGridModel(), $("#instructor-course-list")[0]);
    });
});