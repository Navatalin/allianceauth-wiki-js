import json
import os

from django.contrib.auth.models import User

from wikijs.manager import WikiJSManager, get_wikijs_email

manager = WikiJSManager()
user_groups_query = """query getUserGroups($uid: Int!) {
  users { single(id: $uid) { groups { id name } } }
}"""

for username, expected_group in (
    (os.getenv("AA_ADMIN_USERNAME", "admin"), "Administrators"),
    ("wiki_reader", "WikiReader"),
    ("wiki_editor", "WikiEditor"),
):
    user = User.objects.select_related("profile__main_character").get(username=username)
    if not user.has_perm("wikijs.access_wikijs"):
        raise RuntimeError(f"{username} does not have wikijs.access_wikijs")

    email = get_wikijs_email(user)
    password = manager.activate_user(user)
    if not password:
        raise RuntimeError(f"Wiki.js account activation failed for {username}; check the Alliance Auth log")

    user.refresh_from_db()
    response = json.loads(manager.client.execute(user_groups_query, variables={"uid": user.wikijs.uid}))
    wiki_user = response.get("data", {}).get("users", {}).get("single")
    wiki_groups = {group["name"] for group in wiki_user["groups"]} if wiki_user else set()
    fixture_groups = {"Administrators", "WikiReader", "WikiEditor"}
    if wiki_groups & fixture_groups != {expected_group}:
        raise RuntimeError(f"{username} has unexpected Wiki.js groups: {wiki_groups}")

    print(f"Alliance Auth user: {username}")
    print(f"Main character ID: {user.profile.main_character.character_id}")
    print(f"Wiki.js user ID: {user.wikijs.uid}")
    print(f"Wiki.js group: {expected_group}")
    print(f"Wiki.js login: {email}")
    print(f"Wiki.js password: {password}")

print("Wiki.js integration validation passed")