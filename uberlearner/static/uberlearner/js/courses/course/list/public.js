require([
    'jquery',
    'ko',
    'uberlearner/js/courses/models',
    'uberlearner/js/utils/bindings/url-list',
    'bootstrap',
    'uberlearner/js/courses/course/list/bindings/isotope',
    'uberlearner/js/utils/messages/viewmodel'
], function($, ko, courseModels, courseTileTemplate) {
    $(function() {
        var courseListTilesViewModelGenerator = function() {
            /* Variable Declarations */
            var url = ko.observable();
            var urlData = {
                limit: 12,
                offset: 0
            };
            var courses = ko.observableArray([]);
            var isotope = ko.observable();
            var loading = ko.observable(false);

            /* Helper methods */
            var getDataFromServer = function() {
                $.ajax({
                    url: url(),
                    data: urlData,
                    beforeSend: function(jqXHR, settings) {
                        loading(true);
                    },
                    success: function(data, textStatus, jqXHR) {
                        $.each($.map(data.objects, function(course, index) {
                            return new courseModels.Course(course);
                        }), function(index, course) {
                            courses.push(course);
                        });
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log("response text: " + jqXHR.responseText);
                        console.log("textStatus: " + textStatus);
                        console.log("error: " + errorThrown);
                    },
                    complete: function() {
                        loading(false);
                    }
                });
            };

            /* Subscriptions and events */
            url.subscribe(function(newUrl) {
                getDataFromServer();
            });
            var courseAdded = function(courseTile) {
                if (courseTile && courseTile.nodeType === 1) {
                    $('#tile-container').isotope('appended', $(courseTile), function() {
                        $('#tile-container').isotope('reLayout');
                    });
                }
            };

            /* Controller methods */
            var loadMoreCourses = function() {
                urlData.offset += urlData.limit;
                getDataFromServer();
            };
            var sortAsPopularFirst = function() {
                isotope({
                    sortBy: 'popularity',
                    sortAscending: false
                });
            };
            var sortAsNewestFirst = function() {
                isotope({
                    sortBy: 'dateCreated',
                    sortAscending: false
                });
            };
            var sortAsTopRatedFirst = function() {
                isotope({
                    sortBy: 'rating',
                    sortAscending: false
                });
            };

            /* View related methods */
            var loadMoreButtonText = ko.computed(function() {
                if (courses().length === 0) {
                    return "Unfortunately, No courses exist at the moment";
                } else if (loading()) {
                    return "LOADING...";
                } else {
                    return "LOAD MORE COURSES";
                }
            });

            /* Initialize */
            var _init = function() {
                isotope({
                    layoutMode: 'masonry',
                    itemSelector: '.course-tile',
                    animationEngine: 'best-available',
                    getSortData: {
                        popularity: function($elem) {
                            var course = ko.dataFor($elem.context);
                            return course.popularity;
                        },
                        dateCreated: function($elem) {
                            var course = ko.dataFor($elem.context);
                            return course.creationTimePrecise;
                        },
                        rating: function($elem) {
                            var course = ko.dataFor($elem.context);
                            return course.overallWeightedRating();
                        }
                    }
                });
            }();

            /* Return publicly accessible stuff */
            return {
                url: url,
                courses: courses,
                courseAdded: courseAdded,
                isotope: isotope,
                loadMoreCourses: loadMoreCourses,
                loading: loading,
                sortAsPopularFirst: sortAsPopularFirst,
                sortAsNewestFirst: sortAsNewestFirst,
                sortAsTopRatedFirst: sortAsTopRatedFirst,
                loadMoreButtonText: loadMoreButtonText
            };
        };
        var courseListTilesViewModel = courseListTilesViewModelGenerator();
        ko.applyBindings(courseListTilesViewModel, $('#isotope-envelope')[0]);
    });
});