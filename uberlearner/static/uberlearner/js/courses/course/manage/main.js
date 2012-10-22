require([
    'ko',
    'jquery',
    'uberlearner/js/courses/course/manage/viewmodel',
    'tinymce',
    'ko_tinymce',
    'jquery_tinymce',
    'bootstrap',
    'uberlearner/js/utils/bindings/url-list'
], function(ko, $, ManageCourseViewModel) {
    $(function() {
        ko.applyBindings(new ManageCourseViewModel());
    });
});