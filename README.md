# Description #

Uberlearner is a free web-platform for creating online courses. These courses can contain text, videos, images, quizzes etc.
The objective is to promote community driven educational content with assessment.

The end-goal is to make it like wikipedia with assessment (and its analysis).

# Goals #

This project started off as a commercial venture with the goal of making education cheap and giving the content creators
an incentive to produce good-quality content (using revenue). But over-time, it has evolved to be an open-source platform
with the sole intention of making educational material more accessible to users.

The eventual goal is to:
- Have great assessment tools
- Have analytics related to the assessment to let both the students and teachers know what needs to be improved
- Provide tools for collaborating with other users to make courses better

The exact nature of some of these features is yet to be figured out.

# Installation Instructions #

Coming soon!

# Where to get help #

The Uberlearner.com has a user feedback tab at the bottom right corner for problems related to the usability of the
product.

For bugs, please file a bug-report on the [github issue tracker](https://github.com/Uberlearner/uberlearner/issues).

I will be working on getting a forum or mailing-list working soon!

# Contribution Guidelines #

Coming soon!

# Contributor list #

- Abhin Chhabra (@abhin_chhabra)

# Credits #

This project uses a lot of open-source libraries:

## Server-side ##

- Django : The best web-framework I've had a chance to work with
- South : The database migration tool
- PIL and Pillow : For image manipulation
- Django-allauth : For authentication and account management
- django-bootstrap-toolkit : For making forms play well with bootstrap
- django-recaptcha : For human verification
- django-avatar : For the profile avatar management
- django-ses : For sending emails through Amazon's Simple Email Service (SES)
- django-tastypie : The best REST framework I've used
- django-storages : For storing files using Amazon's Simple Storage Service (S3)
- easy-thumbnails : For creating thumbnails from images
- python-magic : For file type detection
- hoover : For logging to loggly
- python-json-logger : For converting logs to json format
- django-ratings : For managing ratings on the site
- Python : For being a wonderful language to program in

## Front-end ##

**Javascript related:**
- jquery : For making DOM manipulation easy
- jquery-ui : For the extra widgets
- knockoutjs : For making the JS code organized and for being easy to understand
- ckeditor : For the WYSIWYG editor
- isotope : For making the course tiles sexy
- requireJS : For making my JS file dependencies

**HTML/CSS related:**
- Twitter Bootstrap : For being an amazing foundation to work off-of for a HTML/CSS noob
- Font-awesome : For providing extra icons on top of twitter-bootstrap
- lesscss : For making css suck less