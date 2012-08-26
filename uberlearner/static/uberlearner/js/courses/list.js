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
/*
$(function() {
	function CourseListViewModel() {
		var self = this;
		self.courses = ko.observableArray();
		self.meta = ko.observable();
		self.pageSize = 10;
		self.url = '/api/v1/course/';
		self.sortingOptions = [
		    { name: 'Title', fields: ['title']},
		    { name: 'Instructor name', fields: ['instructor']},
		    { name: 'Oldest first', fields: ['creation_timestamp']},
		    { name: 'Newest first', fields: ['-creation_timestamp']},
		    { name: 'Popularity', fields: ['-popularity']}
		];
		self.currentSortingOption = ko.observable();
		self.currentPage = ko.observable(0);
		
		//behaviour
		self.refreshTable = function(url, offset) {
			url = url || self.url;
			var options = {'order_by': self.currentSortingOption().fields[0]};
			if (typeof(offset)!=='undefined')
				options['offset'] = offset
			$.get(url, options, self.loadData);
		};
		self.loadData = function(data) {
			self.courses(data.objects);
			self.meta(data.meta);
		};
		self.loadFirstPage = function() {
			self.refreshTable();
			self.currentPage(0);
		}
		self.loadLastPage = function() {
			var pageIndexes = self.pageIndexes();
			var lastPageIndex = pageIndexes[pageIndexes.length-1];
			var offset = lastPageIndex * self.pageSize;
			self.refreshTable(null, offset);
			self.currentPage(lastPageIndex);
		}
		self.loadPreviousPage = function() {
			if (self.meta() && self.currentPage() > 0) {
				self.refreshTable(self.meta().previous);
				self.currentPage(self.currentPage()-1);
			}
		};
		self.loadNextPage = function() {
			if (self.meta()) {
				self.refreshTable(self.meta().next);
				self.currentPage(self.currentPage()+1);
			}
		};
		self.loadPage = function(index) {
			var offset = index*self.pageSize;
			self.refreshTable(null, offset)
			self.currentPage(index);
		};
		self.hasPreviousPage = ko.computed(function() {
			return self.meta() && self.meta().previous != null;
		});
		self.hasNextPage = ko.computed(function() {
			return self.meta() && self.meta().next != null;
		});
		self.pageIndexes = ko.computed(function() {
			if(self.meta()) {
				pages = []
				var pageCount = Math.ceil(self.meta().total_count / self.pageSize);
				for (var pageIdx=0; pageIdx<pageCount; pageIdx++)
					pages.push(pageIdx);
				return pages;
			} else {
				return [];
			}
		});
		self.changeSortingOption = ko.computed({
			read: function() {
				return self.currentSortingOption();
			},
			write: function(value) {
				self.currentSortingOption(value);
				self.refreshTable();
				self.currentPage(0);
			}
		});
		
		//init
		var init = function() {
			self.changeSortingOption(self.sortingOptions[4]);
		}();
	};
	
	ko.applyBindings(new CourseListViewModel());
});
*/