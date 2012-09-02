/*
$(function() {
    $('#page-content').tinymce({
        script_url: "/static/lib/tiny_mce/tiny_mce.js",
        theme: "advanced",
        mode: "textareas",
        theme_advanced_resizing: true
    });
});
*/

var ManageCourseViewModel = {
    pageContent: ko.observable()
};

ko.applyBindings(ManageCourseViewModel, $('#page-content')[0]);