/*
 Currently, to reach the first milestone, the ajax-based-page-loading will not be implemented. In the first version
 page loading will be conventional to reduce complexity. In the future, when ajax-based-loading is implemented, the
 page could look something like the following:

require(['jquery', 'ko', 'uberlearner/js/courses/page/list/viewmodel', 'bootstrap'], function($, ko, viewModelFactory) {
    $(function() {
        ko.applyBindings(viewModelFactory()); //we apply the view-model page-wide for now
    });
});
*/

require(['jquery', 'bootstrap'], function($) {

});