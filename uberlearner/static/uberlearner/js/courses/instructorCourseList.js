var InstructorCoursesPagedGridModel = function() {
	var self = this;
	
	self.gridViewModel = new ko.uberGrid.viewModel({
		pageSize: 10,
		sortingOptions: [
		    { name: 'Title', field: 'title'},
		    { name: 'Oldest first', field: 'creation_timestamp'},
		    { name: 'Newest first', field: '-creation_timestamp'},
		    { name: 'Popularity', field: '-popularity'}
		],
		columns: [
		    { headerText: "Title", field: "title", link: "absolute_url" },
		    { headerText: "Created on", field: 'creation_timestamp' },
		    { headerText: "Popularity", field: 'popularity' }
		],
		defaultSortingOptionIndex: 3,
		defaultText: 'No courses taught by this instructor could be found!'
	});
};

ko.applyBindings(new InstructorCoursesPagedGridModel(), $("#instructor-course-list")[0]);