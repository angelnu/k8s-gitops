# Setting a user as admin

1. Log into paperless container
2. `python manage.py shell`
3. ```
   from django.contrib.auth.models import User
   user = User.objects.get(username="myname")
   user.is_staff = True
   user.is_admin = True
   user.is_superuser  = True
   user.save()
   ```