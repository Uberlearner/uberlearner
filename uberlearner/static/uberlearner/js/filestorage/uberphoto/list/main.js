require([
    'jquery',
    'ko',
    'uberlearner/js/filestorage/uberphoto/list/viewmodel',
    'uberlearner/js/utils/bindings/url-list'
], function($, ko, viewModelFactory){
    $(function() {
        ko.applyBindings(viewModelFactory()); //apply the viewModel binding page-wide for now
    });
});