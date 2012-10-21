require([
    'ko',
    'jquery',
    'uberlearner/js/courses/course/manage/viewmodel',
    'tinymce',
    'ko_tinymce',
    'jquery_tinymce',
    'bootstrap'
], function(ko, $, ManageCourseViewModel) {
    $(function() {
        ko.applyBindings(new ManageCourseViewModel(), $('#course-management-block')[0]);
    });
});