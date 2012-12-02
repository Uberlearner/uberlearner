require([
    'ko',
    'jquery',
    'uberlearner/js/courses/course/manage/viewmodel',
    'ckeditor',
    'uberlearner/js/utils/bindings/ko.ckeditor',
    'bootstrap',
    'uberlearner/js/utils/bindings/url-list'
], function(ko, $, ManageCourseViewModel) {
    $(function() {
        ko.applyBindings(new ManageCourseViewModel());
    });
});