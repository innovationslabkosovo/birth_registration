Create RapidSms App
====================

To setup and create a new RapidSMS application follow the link below. 
http://kosovoinnovations.org/blog/setup-and-create-rapidsms-app

To install birthreg app, follow these steps:
1.  Create a folder in your new rapidsms project and copy the contents of the birthreg folder.
2.  Add  'birthreg'  to your  INSTALLED_APPS  and  SMS_APPS  in settings.py file.
3.  Run the command  manage.py syncdb.
The release of rapidsms-birthreg is designed to work with Django 1.3 and higher versions. 

Template Integration
=====================
To integrate templates for the birthreg app:

1. Create a “templates” folder inside your rapidsms project
2. Specify template folder in settings.py file
 TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
   os.path.join(os.getcwd(), "templates"),
)
3. Specify url patterns to match the view function in views.py file
urlpatterns = patterns('',
(r'^locations/', birthreg.views.locations), 
)
4. Link view function with the html file
def locations(req):
		…
		…
		…
		return render_to_response(
       			 "birthreg/locations.html", {       
					…
					…
			  }
