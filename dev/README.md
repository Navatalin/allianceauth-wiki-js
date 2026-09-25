# Local validation environment

This environment runs Alliance Auth from the repository virtual environment and
runs Wiki.js, PostgreSQL, and Redis in Docker. The plugin is installed editable,
so Python source changes are available after the Alliance Auth development server
reloads.

## Bootstrap

From the repository root:

```powershell
.\dev\bootstrap.ps1
```

Open <http://localhost:3000> and complete the Wiki.js setup wizard. Use
`http://localhost:3000` as the site URL. In Wiki.js, open **Administration > API
Access**, enable the API, save the setting, and create a Full Access API key.
Creating a key alone is not sufficient while the API toggle remains disabled.

Copy the environment template and add that key:

```powershell
Copy-Item dev\.env.example dev\.env
```

`dev/.env` is ignored by Git.

## Run Alliance Auth

Start it from PowerShell:

```powershell
.\dev\start-auth.ps1
```

Alternatively, run the `Alliance Auth: Local Wiki.js` VS Code debug profile.
Alliance Auth is available at <http://localhost:8000>.

The bootstrap creates this local-only fixture:

- Username: `admin`
- Password: `local-development-password`
- Main character: `Local Wiki Admin` (`90000001`)
- Group: `Wiki-Admin`

It also creates two non-staff users with the same local-only password:

| Username | Main character | Alliance Auth group | Wiki.js group |
| --- | --- | --- | --- |
| `wiki_reader` | `Local Wiki Reader` (`90000002`) | `Wiki-Reader` | `WikiReader` |
| `wiki_editor` | `Local Wiki Editor` (`90000003`) | `Wiki-Editor` | `WikiEditor` |

Both groups have `wikijs.access_wikijs`. Group names lose punctuation when the
plugin maps them to Wiki.js. The plugin creates and assigns the Wiki.js groups,
but their page and action permissions must be configured in Wiki.js to test
reader versus editor access. These fake characters do not provide EVE SSO login.

The admin account can log in at <http://localhost:8000/admin/> without EVE SSO.
To test real OAuth, replace the `AA_ESI_*` values in `dev/.env` with a development
application whose callback is `http://localhost:8000/sso/callback`.

After generating the Wiki.js API key, restart Alliance Auth and use its admin to
grant or inspect the `wikijs.access_wikijs` permission. The fixture already has
this permission through `Wiki-Admin`.

## Validate provisioning

Run the end-to-end validation after adding the API key:

```powershell
.\dev\validate-integration.ps1
```

This creates or reactivates all three seeded users in Wiki.js, verifies each
user's group membership through the Wiki.js API, and prints their generated
Wiki.js logins and passwords. Each run resets all three Wiki.js passwords.

If validation reports `API is disabled`, enable and save API access in Wiki.js
before rerunning the command.

The plugin provisions a local Wiki.js account. It does not configure Wiki.js to
use Alliance Auth as an OAuth or SSO identity provider. Users sign in to Wiki.js
with the generated `{character_id}@wiki.invalid` login and password.

## Recommended user flow

1. Grant `wikijs.access_wikijs` through an Alliance Auth group or state.
2. The user opens **Services** in Alliance Auth and activates Wiki.js.
3. Alliance Auth displays both the `{character_id}@wiki.invalid` login and a
   generated password once on the credentials page.
4. The login remains visible on the user's Alliance Auth Services card.
5. The user can set a chosen password or reset it from that Services card. A
   reset displays both the login and new password again.

Passwords should only be shown to the authenticated user in Alliance Auth. They
should not be emailed, logged, or stored in Alliance Auth.

## Stop or reset

Stop containers while retaining Wiki.js data:

```powershell
.\dev\stop.ps1
```

Delete all Wiki.js and Redis data and start fresh:

```powershell
docker compose -f dev/compose.yml down --volumes
Remove-Item dev\allianceauth\alliance_auth.sqlite3 -ErrorAction SilentlyContinue
.\dev\bootstrap.ps1
```

The reset removes only data created by this local validation environment.
