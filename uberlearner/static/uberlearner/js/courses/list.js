var CoursesPagedGridModel = function() {
	var self = this;
	
	self.gridViewModel = new ko.uberGrid.viewModel({
		pageSize: 10,
		sortingOptions: [
		    { name: 'Title', field: 'title'},
		    { name: 'Instructor name', field: 'instructor'},
		    { name: 'Oldest first', field: 'creation_timestamp'},
		    { name: 'Newest first', field: '-creation_timestamp'},
		    { name: 'Popularity', field: '-popularity'}
		],
		columns: [
		    { headerText: "Title", field: "title", link: "absolute_url" },
		    { headerText: "Instructor", field: function(row) {
		    		return row.instructor.username;
		    	}, link: function(row) {
		    		if (row && row.instructor)
		    			return row.instructor.absolute_url;
		    		else
		    			return '#';
		    	}
		    },
		    { headerText: "Created on", field: 'creation_timestamp' },
		    { headerText: "Popularity", field: 'popularity' }
		],
		defaultSortingOptionIndex: 4,
		defaultText: 'We don\'t have any courses to offer yet. Check again in a few days!'
	});
};

ko.applyBindings(new CoursesPagedGridModel(), $("#course-list")[0]);