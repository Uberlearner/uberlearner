from django.template import RequestContext
from django.views.generic import TemplateView, ListView

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
        image_urls = filter(lambda uberphoto: uberphoto.get_url_dict, images)
        return image_urls

    def get_context_data(self, **kwargs):
        context = super(Browse, self).get_context_data(**kwargs)
        context['images'] = self.get_image_urls(self.request.user)
        return context
