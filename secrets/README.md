# secrets/

OAuth artifacts live here. Both files below are listed in the repo's `.gitignore` — never commit them.

- `credentials.json` — OAuth 2.0 Client ID (type: Desktop app) downloaded from Google Cloud Console.
- `token.json` — auto-generated on first successful OAuth consent. Holds the refresh token.

If you ever want to revoke access:
1. Delete `token.json` here.
2. Revoke the app at <https://myaccount.google.com/permissions>.
