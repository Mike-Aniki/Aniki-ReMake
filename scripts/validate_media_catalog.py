#!/usr/bin/env python3
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "media-catalog.json"
SEMVER_TAG = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
PRESET = re.compile(r"^Login\d+$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not CATALOG.exists():
        fail("media-catalog.json is missing")

    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON: {exc}")

    if data.get("formatVersion") != 1:
        fail("formatVersion must be 1")

    release_tag = data.get("releaseTag")
    if not isinstance(release_tag, str) or not SEMVER_TAG.fullmatch(release_tag):
        fail("releaseTag is missing or invalid")

    items = data.get("items")
    if not isinstance(items, list) or not items:
        fail("items must be a non-empty array")

    preset_keys = set()
    file_names = set()
    random_indexes = set()

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            fail(f"item #{index} is not an object")

        preset = item.get("presetKey")
        name = item.get("name")
        file_name = item.get("fileName")
        size = item.get("size")
        sha256 = item.get("sha256")
        url = item.get("downloadUrl")
        random_index = item.get("randomIndex")

        if not isinstance(preset, str) or not PRESET.fullmatch(preset):
            fail(f"item #{index}: invalid presetKey")
        if preset in preset_keys:
            fail(f"duplicate presetKey: {preset}")
        preset_keys.add(preset)

        if not isinstance(name, str) or not name.strip():
            fail(f"{preset}: name is required")

        if not isinstance(file_name, str) or not file_name.lower().endswith(".mp4"):
            fail(f"{preset}: fileName must be an .mp4")
        if Path(file_name).name != file_name or "/" in file_name or "\\" in file_name:
            fail(f"{preset}: fileName must not contain a path")
        if file_name.lower() in file_names:
            fail(f"duplicate fileName: {file_name}")
        file_names.add(file_name.lower())

        if not isinstance(size, int) or size <= 0:
            fail(f"{preset}: size must be a positive integer")
        if not isinstance(sha256, str) or not SHA256.fullmatch(sha256):
            fail(f"{preset}: sha256 must contain 64 hexadecimal characters")

        if not isinstance(url, str):
            fail(f"{preset}: downloadUrl is required")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
            fail(f"{preset}: downloadUrl must be an HTTPS github.com URL")
        if f"/releases/download/{release_tag}/" not in parsed.path:
            fail(f"{preset}: downloadUrl must use release tag {release_tag}")

        if random_index is not None:
            if not isinstance(random_index, int) or not (1 <= random_index <= 41):
                fail(f"{preset}: randomIndex must be null or between 1 and 41")
            if random_index in random_indexes:
                fail(f"duplicate randomIndex: {random_index}")
            random_indexes.add(random_index)

    print(f"Media catalog OK: {len(items)} optional login background(s).")


if __name__ == "__main__":
    main()
