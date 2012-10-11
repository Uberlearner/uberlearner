require([
    'ko',
    'jquery',
    'uberlearner/js/courses/detail/viewmodel',
    'bootstrap'
], function(ko, $, ViewModel) {
    $(function() {
        ko.applyBindings(new ViewModel(), $('course-detail-block')[0]);
    });
});