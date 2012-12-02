from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView
import magic
from filestorage.models import UberPhoto

class Browse(TemplateView):
    template_name = 'filestorage/browse/index.html'

    def get_image_urls(self, user):
        """
        Gets a list of urls corresponding to the image gallery of the given user.
        This is a list of dictionaries of the format:
        {
            'thumbnail': <thumbnail url>,
            'original': <original url>
        }
        """
        images = user.user_images.all()
        image_urls = map(lambda uberphoto: uberphoto.get_url_dict(), images)
        return image_urls

    def get_context_data(self, **kwargs):
        context = super(Browse, self).get_context_data(**kwargs)
        context['images'] = self.get_image_urls(self.request.user)
        context['main_js_module'] = 'uberlearner/js/filestorage/uberphoto/list/main'
        return context

def is_image_safe(image):
    """
    Checks if the image is safe for consumption.
    """
    allowed_content_types = settings.FILESTORAGE_ALLOWED_CONTENT_TYPES

    if not hasattr(image, 'content_type'):
        return (False, '')

    content_type_from_headers = image.content_type
    mg = magic.Magic(mime=True)
    content_type_from_magic = mg.from_buffer(image.read(1024))
    image.seek(0)

    if not content_type_from_headers in allowed_content_types or not content_type_from_magic in allowed_content_types:
        return (False, 'Files of type {type} are not supported.'.format(type=content_type_from_magic))
    return (True, '')


@csrf_exempt
def upload(request):
    message = ''
    url = ''
    function_number = request.GET['CKEditorFuncNum']
    if request.method == 'POST':
        file = request.FILES['upload']
        if hasattr(file, 'content_type') and file.content_type[:6] == 'image/': #if the content_type starts with "image/"
            image_safety, message = is_image_safe(file)
            if image_safety == True:
                uber_photo_instance = UberPhoto(user=request.user, image=file)
                uber_photo_instance.save()
                url = uber_photo_instance.image.url
                # The image has successfully been uploaded
        else:
            message = 'The uploaded file did not have a mimetype corresponding to an image. Please upload a different version.'

    return render_to_response(
        'filestorage/upload/response.html',
        {
            'message': message,
            'url': url,
            'function_number': function_number
        },
        context_instance=RequestContext(request)
    )