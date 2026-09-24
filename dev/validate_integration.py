import os

from django.contrib.auth.models import User

from wikijs.manager import WikiJSManager, get_wikijs_email

username = os.getenv("AA_ADMIN_USERNAME", "admin")
user = User.objects.select_related("profile__main_character").get(username=username)

if not user.has_perm("wikijs.access_wikijs"):
    raise RuntimeError(f"{username} does not have wikijs.access_wikijs")

email = get_wikijs_email(user)
manager = WikiJSManager()
password = manager.activate_user(user)
if not password:
    raise RuntimeError("Wiki.js account activation failed; check the API key and Alliance Auth log")

user.refresh_from_db()
groups = manager._get_groups()
if not any(group["name"] == "Administrators" for group in groups):
    raise RuntimeError("Wiki.js Administrators group was not created or resolved")

print("Wiki.js integration validation passed")
print(f"Alliance Auth user: {username}")
print(f"Main character ID: {user.profile.main_character.character_id}")
print(f"Wiki.js user ID: {user.wikijs.uid}")
print(f"Wiki.js login: {email}")
print(f"Wiki.js password: {password}")