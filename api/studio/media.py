"""V7.4: real B-roll for the things we talk about (D20). Two sources, both logged in provenance with a licence and an
on-screen credit: Pixabay stock footage/photos (free key, Pixabay Content License) and official Rockstar media
(only files hosted on rockstargames.com, shown briefly as commentary). Every file becomes a 1080x1920 30 fps clip
timed to its scene: videos are cropped to cover, stills get a slow push-in. Trending YouTube videos are never
downloaded (D21). Stdlib + ffmpeg only."""

import json
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

from studio.config import OFFICIAL_MEDIA_DOMAINS, PIXABAY_API_KEY

UA = {"User-Agent": "trend-radar-studio/1.0 (b-roll fetch; owner-reviewed, nothing auto-published)"}
PIXABAY_LICENSE = "Pixabay Content License (free for commercial use; no attribution required, credited anyway)"
PIXABAY_LICENSE_URL = "https://pixabay.com/service/license-summary/"
ROCKSTAR_LICENSE = "© Rockstar Games / Take-Two; official media hosted on rockstargames.com, brief commentary use with credit (D20)"
OG_IMAGE = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', re.I)
OG_IMAGE_REV = re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', re.I)


def _get(url: str, timeout: int = 30) -> tuple[bytes, str]:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def _official_host(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return urllib.parse.urlparse(url).scheme == "https" and any(host == d or host.endswith("." + d) for d in OFFICIAL_MEDIA_DOMAINS)


def pixabay(query: str, out_dir: Path) -> dict | None:
    """Best Pixabay hit for `query`: a video when there is one, else a vertical photo, else any photo.
    -> {path, page, by, kind, credit} or None when nothing matches."""
    if not PIXABAY_API_KEY:
        raise RuntimeError("PIXABAY_API_KEY is not set (free key: https://pixabay.com/api/docs/)")
    q = urllib.parse.quote_plus(query)
    base = f"key={PIXABAY_API_KEY}&q={q}&safesearch=true&per_page=5"
    body, _ = _get(f"https://pixabay.com/api/videos/?{base}")
    for h in json.loads(body)["hits"]:
        v = h["videos"].get("medium") or h["videos"].get("small") or h["videos"]["large"]
        return _save(v["url"], out_dir / f"pixabay-{h['id']}.mp4", h, "video")
    for extra in ("&orientation=vertical&image_type=photo", "&image_type=photo"):
        body, _ = _get(f"https://pixabay.com/api/?{base}{extra}")
        for h in json.loads(body)["hits"]:
            return _save(h["largeImageURL"], out_dir / f"pixabay-{h['id']}.jpg", h, "image")
    return None


def _save(url: str, path: Path, hit: dict, kind: str) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    data, _ = _get(url, timeout=120)
    path.write_bytes(data)
    return {"path": str(path), "page": hit["pageURL"], "by": hit["user"], "kind": kind,
            "credit": f"{'Footage' if kind == 'video' else 'Photo'}: Pixabay · {hit['user']}"}


def official(url: str, out_dir: Path) -> dict:
    """An official Rockstar image: the URL itself when it is an image, else the page's og:image. Both must be
    hosted on rockstargames.com (OFFICIAL_MEDIA_DOMAINS); anything else is refused."""
    if not _official_host(url):
        raise ValueError(f"not an official media URL (must be https on {', '.join(OFFICIAL_MEDIA_DOMAINS)}): {url}")
    data, ctype = _get(url)
    page = url
    if not ctype.startswith("image/"):
        html = data.decode("utf-8", "replace")
        m = OG_IMAGE.search(html) or OG_IMAGE_REV.search(html)
        if not m:
            raise ValueError(f"no image found on {url}")
        url = urllib.parse.urljoin(page, m[1])
        if not _official_host(url):
            raise ValueError(f"the page's image is not hosted by Rockstar: {url}")
        data, ctype = _get(url)
        if not ctype.startswith("image/"):
            raise ValueError(f"not an image: {url} ({ctype})")
    ext = {"image/png": "png", "image/webp": "webp"}.get(ctype.split(";")[0], "jpg")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"rockstar-{abs(hash(url)) % 10**8}.{ext}"
    path.write_bytes(data)
    return {"path": str(path), "page": page, "by": "Rockstar Games", "kind": "image", "credit": "Image: Rockstar Games"}


COVER = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"


def to_clip(src: str | Path, seconds: float, out: Path) -> Path:
    """A silent 1080x1920 30 fps H.264 clip of `seconds`: videos loop if shorter and are cropped to cover;
    stills get a slow push-in (zoompan on a 1.5x pre-scale, so the zoom stays sharp)."""
    frames = max(1, round(seconds * 30))
    if Path(src).suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        vf = (f"scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,"
              f"zoompan=z='min(zoom+0.0006,1.09)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", vf, "-frames:v", str(frames)]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{seconds:.3f}", "-vf", f"{COVER},fps=30"]
    subprocess.run([*cmd, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)],
                   check=True, stdin=subprocess.DEVNULL, capture_output=True)
    return out


def third_party_share(scenes: list[dict]) -> float:
    """Seconds on fetched media (shot "broll") over the whole track: the D20 gate (config THIRD_PARTY_MAX_SHARE)."""
    total = scenes[-1]["end"] - scenes[0]["start"] if scenes else 0
    return round(sum(s["end"] - s["start"] for s in scenes if s["shot"] == "broll") / total, 3) if total else 0.0
