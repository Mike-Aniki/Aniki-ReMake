# Optional Login Background Media

Aniki Helper downloads Aniki ReMake Login Screen background videos only when the user selects them. Downloaded media and the user custom video are kept in Aniki Helper data so a theme update cannot delete the only copy.

## Files kept inside the theme

Keep the core/default media in `Startup Video`, including:

- `Acceuil.mp4`
- `Glitch.mp4`
- `LuckyDay.mp4`
- `LuckyDay2.mp4`
- `Startup.mp4`
- `Startup_LuckyDay1.mp4`
- `Startup_LuckyDay2.mp4`
- `Shutdown.mp4`
- `Shutdown_LuckyDay1.mp4`
- `Shutdown_LuckyDay2.mp4`

`Acceuil Yakuza6.mp4` was an obsolete duplicate of `Kazuma Kiryu.mp4` in the old Random list and is no longer required. `AcceuilAkatsuki.mp4` is now a normal optional Login Background and is included in the release catalog.

The videos listed in `media-catalog.json` are optional and can be removed from the distributed theme package after the release assets have been uploaded.

## First upload

1. Copy `media-catalog.json`, `scripts/`, and `.github/workflows/validate-media-catalog.yml` into the Aniki-ReMake repository.
2. Commit and push them.
3. Install GitHub CLI and authenticate with `gh auth login` if needed.
4. From the repository, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish-login-background-media.ps1 -ThemeFolder "C:\Path\To\Aniki ReMake"
```

The script verifies every file against the catalog and uploads all optional Login Background MP4 files to the `login-backgrounds-v1` GitHub Release.

## Runtime behavior

- If the selected Login background is already present, Aniki Helper applies it normally.
- Existing optional videos are adopted into the persistent Helper library. On NTFS and on the same volume this uses hard links, so the Helper and theme paths do not use double disk space.
- If a theme update removes a theme-side video, Aniki Helper recreates the hard link automatically. If hard links are unavailable, it falls back to a normal copy.
- If a selected optional video is not installed, Aniki Helper offers to download it, verifies its size and SHA-256, stores it in the persistent library, then exposes it again under `Startup Video`.
- Random Login uses only normal indexed videos actually present locally.
- `ClairObscur.mp4` now occupies Random index 19; the obsolete Yakuza 6 duplicate was removed.
- `AcceuilAkatsuki.mp4` remains Random index 26 and now also has a normal selectable preset.
- `CustomLogin.mp4` uses Random index 43 only when the user has configured a Custom Login Video from Aniki Helper Desktop settings.
- Random index 42 is reserved exclusively for the Lucky Day easter egg and is never part of the normal Random pool.
- `Acceuil.mp4` remains the fallback when no normal Random background is installed.
