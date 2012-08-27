var PopularCourses = function() {
	var self = this;
	
	self.gridViewModel = new ko.uberGrid.viewModel({
		pageSize: 5,
		columns: [
		    { headerText: "Title", field: "title", link: "absolute_url" },
		    { headerText: "Instructor", field: function(row) {
		    		return row.instructor.username;
		    	}, link: function(row) {
	    			return row.instructor.absolute_url;
		    	}
		    },
		    { headerText: "Created on", field: 'creation_timestamp' },
		    { headerText: "Popularity", field: 'popularity' }
		],
		defaultText: 'We don\'t have any courses to offer yet. Check again in a few days!'
	});
};

var NewCourses = function() {
	var self = this;
	
	self.gridViewModel = new ko.uberGrid.viewModel({
		pageSize: 5,
		columns: [
		    { headerText: "Title", field: "title", link: "absolute_url" },
		    { headerText: "Instructor", field: function(row) {
		    		return row.instructor.username;
		    	}, link: function(row) {
	    			return row.instructor.absolute_url;
		    	}
		    },
		    { headerText: "Created on", field: 'creation_timestamp' },
		    { headerText: "Popularity", field: 'popularity' }
		],
		defaultText: 'We don\'t have any courses to offer yet. Check again in a few days!'
	});
};

ko.applyBindings(new PopularCourses(), $("#popular-course-list")[0]);
ko.applyBindings(new NewCourses(), $("#new-course-list")[0]);