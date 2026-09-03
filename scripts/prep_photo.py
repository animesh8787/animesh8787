#!/usr/bin/env python3
"""
prep_photo.py - cut the background out of a photo and crop it to a
head-and-shoulders square, ready for dotify.py.

    pip install rembg          # one-time, ~large; downloads a model on first run
    python scripts/prep_photo.py photo.jpeg
    python scripts/dotify.py me-cutout.png -o assets/portrait \
        --cols 100 --equalize --detail 0.5 --color --reveal

Why bother: dotify treats an alpha channel as a subject mask, so nothing is
drawn outside you AND --equalize then measures only you instead of averaging in
a busy background. It is the single biggest quality win for the portrait.

Output: me-cutout.png (RGBA, transparent background). Gitignored - the
committed artefact is assets/portrait.svg, not the photo.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps

MARGIN = 0.12  # padding around the detected subject, as a fraction of its size


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]
    if not argv:
        sys.exit("usage: python scripts/prep_photo.py <photo>")
    src = Path(argv[0])
    out = Path(argv[1]) if len(argv) > 1 else Path("me-cutout.png")
    if not src.exists():
        sys.exit(f"no such file: {src}")

    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")

    try:
        from rembg import new_session, remove
    except ImportError:
        sys.exit(
            "rembg is not installed.\n"
            "  pip install rembg\n"
            "(or cut the background out in any editor and save a transparent PNG"
            " as me-cutout.png yourself.)"
        )

    print("removing background (first run downloads a model)...")
    cut = remove(img, session=new_session("u2netp"), post_process_mask=True)

    # Head-and-shoulders square crop. A selfie's bounding box is dragged wide by
    # the arm holding the phone, so centring on the bbox puts the face off to one
    # side. Instead: centre horizontally on the head (the mask's centre of mass
    # in its top slice) and anchor the square just above the top of the head.
    alpha = cut.split()[3]
    box = alpha.getbbox()
    if box:
        l, t, r, b = box
        subj_h = b - t
        head = alpha.crop((l, t, r, t + max(1, subj_h // 4)))
        px = head.load()
        sx = sn = 0
        for y in range(head.height):
            for x in range(head.width):
                if px[x, y] > 128:
                    sx += x
                    sn += 1
        head_cx = l + (sx / sn if sn else (r - l) / 2)

        side = min(cut.height - t + int(subj_h * MARGIN),
                   int(subj_h * 1.15))
        top = max(0, t - int(subj_h * MARGIN))
        left = int(head_cx - side / 2)
        left = max(0, min(left, cut.width - side))
        side = min(side, cut.width - left, cut.height - top)
        cut = cut.crop((left, top, left + side, top + side))

    if cut.width != cut.height:
        side = max(cut.size)
        square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        square.paste(cut, ((side - cut.width) // 2, (side - cut.height) // 2))
        cut = square

    cut.save(out)
    print(f"wrote {out}  ({cut.width}x{cut.height}, transparent background)")


if __name__ == "__main__":
    main()
