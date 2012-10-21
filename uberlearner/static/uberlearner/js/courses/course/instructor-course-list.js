require(['jquery', 'ko', 'uberGrid', 'bootstrap'], function($, ko, uberGrid, bootstrap) {
    var InstructorCoursesPagedGridModel = function() {
        var self = this;

        self.gridViewModel = new uberGrid.viewModel({
            pageSize: 10,
            sortingOptions: [
                { name: 'Title', field: 'title'},
                { name: 'Oldest first', field: 'creation_timestamp'},
                { name: 'Newest first', field: '-creation_timestamp'},
                { name: 'Popularity', field: '-popularity'}
            ],
            columns: [
                { headerText: "Title", field: "title", link: "absoluteUrl" },
                { headerText: "Created on", field: 'creationTimestamp' },
                { headerText: "Popularity", field: 'popularity' }
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