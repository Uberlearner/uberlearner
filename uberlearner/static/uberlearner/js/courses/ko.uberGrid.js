(function () {
	ko.uberGrid = {
		viewModel: function (configuration) {
			var self = this;
			self.url = ko.observable('')
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
			
			self.currentPageIndex = ko.observable(0);
			self.currentSortingOption = ko.observable(self.sortingOptions ? self.sortingOptions[self.defaultSortingOptionIndex] : undefined);
			self.currentDataOptions = ko.computed(function() {
				if (self.url() == '') {
					// if the url hasn't been set by the binding yet, then don't waste time on ajax call
					return;
				};
				var options = self.extraGetParams();
				options[self.offsetGetKey] = self.pageSize*self.currentPageIndex();
				if (self.currentSortingOption() && self.currentSortingOption().field)
					options[self.orderingGetKey] = self.currentSortingOption().field;
				options[self.limitGetKey] = self.pageSize;
				
				//TODO: find a better way of updating the currentData
				$.get(self.url(), options, function(data) {
					self.currentData(data.objects);
					self.currentMeta(data.meta);
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
			self.currentData = ko.observable([]);
			self.currentMeta = ko.observable({});
			
			self.maxPageIndex = ko.computed(function () {
				var totalCount = self.currentMeta().total_count || 0;
				if (totalCount == 0)
					return 0;
				else {
                    _maxPageIndex = Math.floor(totalCount/self.pageSize);
                    if (self.maxPageCount != -1)
                        _maxPageIndex = Math.min(_maxPageIndex, self.maxPageCount);

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
				return self.currentMeta().total_count > 0;
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
			self.getTdHtml = function(rowData, columnConfig) {
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
	
	templateEngine.addTemplate = function(templateName, templateMarkup) {
		document.write("<script type='text/html' id='" + templateName + "'>" + templateMarkup + "</script>");
	};
	
	templateEngine.addTemplate("ko_uberGrid_sortingOptions", 
			"<div class=\"row\" data-bind=\"visible: showSortingOptions()\">" +
			"	<div class=\"span2 offset6\">" +
			"		<label> Sort by:" +
			"			<select data-bind=\"options: sortingOptions," +
			"								optionsText: \'name\'," +
			"								value: changeSortingOption\">" +
			"			</select>" +
			"		</label>" +
			"	</div>" +
			"</div>");
	templateEngine.addTemplate("ko_uberGrid_grid", 
			"<div class=\"row\">" +
			"	<table class=\"table table-striped table-bordered\" data-bind=\"visible: dataExists\">" +
			"		<thead>" +
			"			<tr data-bind=\"foreach: columns\">" +
			"				<th data-bind=\"text: $data.headerText\"></th>" +
			"			</tr>" +
			"		</thead>" +
			"		<tbody data-bind=\"foreach: currentData\">" +
			"			<tr data-bind=\"foreach: $root.columns\">" +
			"				<td data-bind=\"html: $root.getTdHtml($parentContext.$data, $data)\">" +
			"				</td>" +
			"			</tr>" +
			"		</tbody>" +
			"	</table>" +
			"</div>");
	templateEngine.addTemplate("ko_uberGrid_pageLinks", 
			"<div class=\"row\" data-bind=\"visible: dataExists() && maxPageIndex() > 0\">" +
			"	<div class=\"span2\">" +
			"		<a href=\"javascript: void(0);\" data-bind=\"" +
			"			visible: hasPrevious, " +
			"			click: function() { currentPageIndex(0) }\">" +
			"			First" +
			"		</a>&nbsp;&nbsp;" +
			"		<a href=\"javascript: void(0);\" data-bind=\"" +
			"			visible: hasPrevious, " +
			"			click: function() { currentPageIndex(currentPageIndex()-1) }\">" +
			"			Previous" +
			"		</a>" +
			"	</div>" +
			"	<div class=\"span4\">" +
			"		<ul class=\"nav nav-pills\" data-bind=\"foreach: ko.utils.range(0, maxPageIndex)\">" +
			"			<li data-bind=\"css: { active: $data == $root.currentPageIndex() }\">" +
			"				<a href=\"javascript: void(0);\" " +
			"					data-bind=\"click: function() { $root.currentPageIndex($data) }, text: $data + 1\">" +
			"				</a>" +
			"			</li>" +
			"		</ul>" +
			"	</div>" +
			"	<div class=\"span2\">" +
			"		<span class=\"pull-right\">" +
			"			<a href=\"javascript: void(0);\" data-bind=\"" +
			"				visible: hasNext, " +
			"				click: function() { currentPageIndex(currentPageIndex()+1) }\">" +
			"				Next" +
			"			</a>&nbsp;&nbsp;" +
			"			<a href=\"javascript: void(0);\" data-bind=\"" +
			"				visible: hasNext, " +
			"				click: function() { currentPageIndex(maxPageIndex()) }\">" +
			"				Last" +
			"			</a>" +
			"		</span>" +
			"	</div>" +
			"</div>");
	templateEngine.addTemplate("ko_uberGrid_defaultText", 
			"<div class=\"row\" data-bind=\"visible: !dataExists()\">" +
			"	<p data-bind=\"text: defaultText\"></p>" +
			"</div>");
	
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
})();