# Shiying source rules

- Keep the parsing submodule at the pinned commit in .gitmodules.
- macOS uses Sources/; Windows uses Desktop/; both share Backend/.
- Never commit logins, user libraries, media, private paths, or generated packages.
- Validate source checks and the actual target-platform package before a release.
- Do not edit a running installed app or its user data during builds.
