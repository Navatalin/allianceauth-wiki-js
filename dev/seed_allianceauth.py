import os

from django.contrib.auth.models import Group, Permission, User

from allianceauth.eveonline.models import EveCharacter

username = os.getenv("AA_ADMIN_USERNAME", "admin")
password = os.getenv("AA_ADMIN_PASSWORD", "local-development-password")
character_id = int(os.getenv("AA_CHARACTER_ID", "90000001"))

user, _ = User.objects.get_or_create(
    username=username,
    defaults={"email": "local-admin@example.invalid"},
)
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

character, _ = EveCharacter.objects.update_or_create(
    character_id=character_id,
    defaults={
        "character_name": "Local Wiki Admin",
        "corporation_id": 98000001,
        "corporation_name": "Local Development Corporation",
        "corporation_ticker": "DEV",
    },
)
user.profile.main_character = character
user.profile.save()

wiki_admin, _ = Group.objects.get_or_create(name="Wiki-Admin")
wiki_admin.permissions.add(Permission.objects.get(codename="access_wikijs"))
user.groups.add(wiki_admin)

print(f"Local Alliance Auth user ready: {username}")
print(f"Main character ID: {character_id}")
print("Wiki.js group: Wiki-Admin -> Administrators")