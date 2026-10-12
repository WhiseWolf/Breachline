# Facebook Page credential import

Target: **Breachline Agent**, Page-ID **1411966515325246**, Meta app
**Breachline-agent**, App-ID **1387499541111305**.

On 2026-10-12 the user confirmed API access for posting and reading comments/
statistics. In Meta's browser UI the app was authorized for this current Page
only. A long-lived User token was generated with user password confirmation;
the Page token was derived from that token. The User token is not distributed.
Meta's Access Token Debugger confirmed the resulting token is **PAGE**, valid,
with **Expires: Never**, and a separate data-access expiration timestamp
**1799561740**. Scopes: `pages_manage_posts`, `pages_read_user_content`,
`pages_read_engagement`, `pages_show_list`, `read_insights`, `public_profile`.

"Never" is the token expiration field, not a guarantee of permanent access.
Revocation, permission/account changes and data-access expiry can still require
reauthentication. Check actual access before use. Do not infer successful posting
from granted scopes or from a successful read. No post was created by this setup.

## Ubuntu import

From `/home/pagi/breachline-agent`:

```bash
git -C repo pull --ff-only origin agent-lab
cp repo/runtime/facebook_import_encrypted.py /tmp/breachline-facebook-import.py
python3 /tmp/breachline-facebook-import.py
python3 repo/runtime/facebook_check.py
```

Enter the short unlock code provided separately in the conversation. The code
and plaintext token are intentionally absent from GitHub. The importer uses
OpenSSL AES-256-CBC/PBKDF2 with a separately derived HMAC-SHA256 key, authenticates
the ciphertext before decryption and saves credentials atomically to
`~/.config/breachline-agent/facebook.json` with file permissions 0600 and folder
permissions 0700. It replaces a previous Facebook credential if present.
Instagram credentials are untouched. On success the executing temporary script
copy deletes itself; the encrypted repository copy remains available.

Requires Python 3 and OpenSSL. No package install is otherwise needed. Wrong
unlock codes preserve the script and any previous credential. Never put the
unlock code on GitHub or print/read credential JSON into Jarvis model context.

## Jarvis status

`python3 repo/runtime/facebook_check.py` can be run through existing `shell_exec`
on the Ubuntu host. It reads the token internally and checks the exact Page ID
and name. No Docker credential mounting or config.toml edit is needed.

This delivers credential import and a real-access check, **not a full Facebook
publishing adapter**. The existing Instagram adapter cannot publish to Facebook.
Posting, comment retrieval and statistics require a separate Facebook adapter
with the project's authorization and durable write receipts. Do not improvise
by printing the token into shell commands, generic http_request calls or logs.

Primary references:
- https://developers.facebook.com/documentation/facebook-login/guides/access-tokens
- https://developers.facebook.com/documentation/facebook-login/guides/access-tokens/get-long-lived
- https://developers.facebook.com/documentation/pages-api/getting-started

The actual browser verification above is the evidence for this token's identity,
scopes and expiry fields. A separate Ubuntu check confirms local import/access.
