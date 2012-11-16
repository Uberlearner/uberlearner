/**
 * This file contains configuration information that applies to all instances of ckeditor on Uberlearner. Any overrides
 * can be made during the initialization of the instance.
 */

CKEDITOR.editorConfig = function( config )
{
    config.skin = 'BootstrapCK-Skin';
    config.toolbar = [
        { name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat', '-', 'TextColor' ] },
        { name: 'paragraph', items : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote','CreateDiv',
            '-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock','-','BidiLtr','BidiRtl' ] },
        { name: 'links', items : [ 'Link','Unlink','Anchor' ] },
        { name: 'editing', items : [ 'Find','Replace','-', 'Scayt' ] },
        { name: 'document', items: [ 'Source' ] },
        // '/',
        { name: 'clipboard', items : [ 'Cut','Copy','Paste','PasteText','PasteFromWord','-','Undo','Redo' ] },
        { name: 'insert', items : [ 'Image', 'Table','HorizontalRule', 'SpecialChar','PageBreak'] },
        { name: 'styles', items : [ 'Styles','Format','Font','FontSize' ] }
    ];
    config.height = '400px';
    config.filebrowserImageBrowseUrl = '/filestorage/browse/';
    config.filebrowserUploadUrl = '/filestorage/upload/';
};