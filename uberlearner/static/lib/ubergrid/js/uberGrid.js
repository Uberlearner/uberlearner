define([
    'jquery',
    'ko',
    'lib/ubergrid/templates/sorting_options',
    'lib/ubergrid/templates/page_links',
    'lib/ubergrid/templates/grid',
    'lib/ubergrid/templates/default_text'
], function ($, ko, courseModels, sortingOptions, pageLinks, grid, defaultText) {
    var uberGrid = {
        viewModel: function (configuration) {
            var self = this;
            self.url = ko.observable('');
            self.pageSize = configuration.pageSize || 10;
            self.maxPageCount = configuration.maxPageCount || -1;
            self.sortingOptions = configuration.sortingOptions || [];
            self.columns = configuration.columns || []; //TODO: the url can be used to get the schema,
            //which can be used to get the column data
            self.orderingGetKey = configuration.orderingGetKey || 'order_by';
            self.offsetGetKey = configuration.offsetGetKey || 'offset';
            self.limitGetKey = configuration.limitGetKey || 'limit';
            self.defaultSortingOptionIndex = configuration.defaultSortingOptionIndex || 0;
            self.extraGetParams = ko.observable({});
            self.defaultText = configuration.defaultText || 'No data for this table could be found!';
            self.dataAdapter = configuration.dataAdapter;

            self.currentPageIndex = ko.observable(0);
            self.currentSortingOption = ko.observable(self.sortingOptions ? self.sortingOptions[self.defaultSortingOptionIndex] : undefined);
            self.currentDataOptions = ko.computed(function() {
                if (self.url() == '') {
                    // if the url hasn't been set by the binding yet, then don't waste time on ajax call
                    return;
                }
                var options = self.extraGetParams();
                options[self.offsetGetKey] = self.pageSize*self.currentPageIndex();
                if (self.currentSortingOption() && self.currentSortingOption().field)
                    options[self.orderingGetKey] = self.currentSortingOption().field;
                options[self.limitGetKey] = self.pageSize;

                //TODO: find a better way of updating the currentData
                $.ajax({
                    url: self.url(),
                    data: options,
                    success: function(data) {
                        self.currentData([]);
                        $.each($.map(data.objects, function(course, index) {
                            return self.dataAdapter(course);
                        }), function(index, course) {
                            self.currentData.push(course);
                        });
                        self.currentMeta(data.meta);
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log("response text: " + jqXHR.responseText);
                        console.log("textStatus: " + textStatus);
                        console.log("error: " + errorThrown);
                    }

                });

                return options;
            });
            self.changeSortingOption = ko.computed({
                read: function() {
                    return self.currentSortingOption();
                },
                write: function(value) {
                    self.currentSortingOption(value);
                    self.currentPageIndex(0);
                }
            });
            self.currentData = ko.observableArray([]);
            self.currentMeta = ko.observable({});

            self.maxPageIndex = ko.computed(function () {
                var totalCount = self.currentMeta().totalCount || 0;
                if (totalCount == 0)
                    return 0;
                else {
                    _maxPageIndex = Math.floor((totalCount-1)/self.pageSize);
                    if (self.maxPageCount != -1)
                        _maxPageIndex = Math.min(_maxPageIndex, self.maxPageCount);
                    if (_maxPageIndex == -1)
                        _maxPageIndex = 0;

                    return _maxPageIndex;
                }
            });

            self.goToFirstPage = function() {
                self.currentPageIndex(0);
            };
            self.goToPageIdx = function(pageIdx) {
                if (pageIdx < 0 || pageIdx > self.maxPageIndex())
                    return;
                self.currentPageIndex(pageIdx);
            };
            self.goToNextPage = function() {
                if (self.currentPageIndex() >= self.maxPageIndex())
                    return;
                self.currentPageIndex(self.currentPageIndex()+1);
            };
            self.goToPreviousPage = function() {
                if (pageIdx <= 0)
                    return;
                self.currentPageIndex(self.currentPageIndex()-1);
            };
            self.goToLastPage = function() {
                if (self.currentPageIndex() >= self.maxPageIndex())
                    return;
                self.currentPageIndex(self.maxPageIndex());
            };
            self.hasNext = ko.computed(function() {
                return self.currentPageIndex() < self.maxPageIndex();
            });
            self.hasPrevious = ko.computed(function() {
                return self.currentPageIndex() > 0;
            });
            self.dataExists = ko.computed(function() {
                return self.currentMeta().totalCount > 0;
            });
            self.pageIndexes = ko.computed(function() {
                indexes = ko.utils.range(0, self.maxPageIndex());
                return indexes;
            });
            /**
             * Returns the html to be filled into each td node in the data-grid.
             * 1) If the link exists, then an anchor tag is used, else text in inputted directly
             * 2) If the link is a function, then it is called, otherwise the link is a key into the row data.
             * 3) If the value is a function, then it is called, otherwise the value is a key into the row data.
             */
            self.getDataHtml = function(rowData, columnConfig) {
                var content = '';
                if (typeof(columnConfig.field) == 'function')
                    content = columnConfig.field(rowData);
                else
                    content = rowData[columnConfig.field];

                if (typeof(columnConfig.link) == 'undefined')
                    return content;
                else {
                    var link = '';
                    if (typeof(columnConfig.link) == 'function')
                        link = columnConfig.link(rowData);
                    else
                        link = rowData[columnConfig.link];

                    return "<a href=\"" + link + "\">" + content + "</a>";
                }
            };
            self.showSortingOptions = function() {
                return self.dataExists() && (self.sortingOptions.length>0);
            }
        }
    };

    // Templates used to render the grid
    var templateEngine = new ko.nativeTemplateEngine();
    /*
    * The following code was required when requirejs was being used to load the templates. But since stupid
    * internet exploder has a problem with that, the html files were converted to js file that insert the
    * appropriate code into the html themselves.
    $(function() {
        [sortingOptions, pageLinks, grid, defaultText].forEach(function(html) {
            $('body').append($(html));
        });
    });
    */

    // The ubergrid url binding
    ko.bindingHandlers.uberGridUrl = {
        update: function(element, valueAccessor, allBindingsAccessor, viewModel) {
            //var url = valueAccessor();
            //viewModel.gridViewModel.url(url);
        }
    };

    // The ubergrid get params binding
    ko.bindingHandlers.uberGridGetParams = {
        update: function(element, valueAccessor, allBindingsAccessor, viewModel) {
            //var getParams = valueAccessor();
            //viewModel.gridViewModel.extraGetParams(getParams);
        }
    };

    // The uberGrid binding
    ko.bindingHandlers.uberGrid = {
        init: function() {
            return {'controlsDescendantBindings': true};
        },
        update: function (element, viewModelAccessor, allBindingsAccessor) {
            var viewModel = viewModelAccessor(), allBindings = allBindingsAccessor();

            // Empty the element
            while(element.firstChild)
                ko.removeNode(element.firstChild);

            // Add the correct url and filter to the view model
            if (typeof(allBindings.uberGridGetParams) != 'undefined')
                viewModel.extraGetParams(allBindings.uberGridGetParams);
            if (typeof(allBindings.uberGridUrl) != 'undefined')
                viewModel.url(allBindings.uberGridUrl);

            // Allow the default template to be over-ridden
            var gridTemplateName = allBindings.uberGridTemplate || "ko_uberGrid_grid";
            var pageLinksTemplateName = allBindings.uberGridPagerTemplate || "ko_uberGrid_pageLinks";
            var sortingOptionsTemplateName = allBindings.uberGridSortingOptionsTemplate || "ko_uberGrid_sortingOptions";
            var defaultTextTemplateName = allBindings.uberGridDefaultTextTemplate || "ko_uberGrid_defaultText";

            // Render the sorting options
            var sortingOptionsContainer = element.appendChild(document.createElement("DIV"));
            ko.renderTemplate(sortingOptionsTemplateName, viewModel, { templateEngine: templateEngine }, sortingOptionsContainer, "replaceNode");

            // Render the main grid
            var gridContainer = element.appendChild(document.createElement("DIV"));
            ko.renderTemplate(gridTemplateName, viewModel, { templateEngine: templateEngine }, gridContainer, "replaceNode");

            // Render the page links
            var pageLinksContainer = element.appendChild(document.createElement("DIV"));
            ko.renderTemplate(pageLinksTemplateName, viewModel, { templateEngine: templateEngine }, pageLinksContainer, "replaceNode");

            // Render the default text
            //var defaultTextContainer = element.appendChild(document.createElement("DIV"));
            //ko.renderTemplate(defaultTextTemplateName, viewModel, { templateEngine: templateEngine }, defaultTextContainer, "replaceNode");

        }
    };

    return uberGrid;
});