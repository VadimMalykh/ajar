"""The music on trial in the sound lab (map SOUND): recorded pieces, local to a
worktree and never committed.

They live in trial/music/ (git-ignored, often 4-8 MB an MP3), with a list
trial/music/tracks.txt: lines `file|Title|what it is for; who made it and the
licence`, `#` comments. make_all(root) takes every audio file there (.mp3 .ogg
.flac .wav .mid; not *.part, still downloading), those listed in the list's
order first and any other after them by name, and gives build.py

    music/AJT01.<ext>, music/AJT02.<ext> ...   the files as they are (build.py
                                               stores them, not deflated)
    ajmusic.txt     one line a track, LUMP|Title|what it is for, read by the
                    lab (src/zscript/soundlab.zs); a file not in the list is
                    named by its file name, and is "your own file"

With no folder or no files, ajmusic.txt has no tracks, and the lab says that
candidates go in trial/music/.

    python3 tools/music_trial.py     prints what a build would take
"""
import os

KINDS = (".mp3", ".ogg", ".flac", ".wav", ".mid")


def tracks(root):
    """[(file, title, what)] in the order they go into the package."""
    folder = os.path.join(root, "trial", "music")
    try:
        files = sorted(f for f in os.listdir(folder)
                       if os.path.splitext(f)[1].lower() in KINDS and os.path.isfile(os.path.join(folder, f)))
    except FileNotFoundError:
        return []
    listed = []
    try:
        with open(os.path.join(folder, "tracks.txt"), encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3 and parts[0] in files and parts[0] not in (l[0] for l in listed):
                    listed.append((parts[0], parts[1], "; ".join(parts[2:])))
    except FileNotFoundError:
        pass
    named = {l[0] for l in listed}
    return listed + [(f, os.path.splitext(f)[0], "your own file") for f in files if f not in named]


def make_all(root):
    """{pk3 path: bytes or text} for build.py."""
    out, listing = {}, []
    for n, (file, title, what) in enumerate(tracks(root), 1):
        lump = f"AJT{n:02d}"
        with open(os.path.join(root, "trial", "music", file), "rb") as f:
            out[f"music/{lump}{os.path.splitext(file)[1].lower()}"] = f.read()
        listing.append(f"{lump}|{title.replace('|', ';')}|{what}")
    out["ajmusic.txt"] = "".join(l + "\n" for l in listing)
    return out


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    t = tracks(root)
    for n, (file, title, what) in enumerate(t, 1):
        size = os.path.getsize(os.path.join(root, "trial", "music", file))
        print(f"AJT{n:02d}  {title}  ({file}, {size / 1e6:.1f} MB)\n       {what}")
    if not t:
        print("no music: candidates go in trial/music/")
