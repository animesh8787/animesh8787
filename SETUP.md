# Setup

This is the config for **`github.com/animesh8787/animesh8787`** — the repo whose
name matches the username, so its `README.md` renders on the profile page.

Built from the walkthrough in *Profile-README-Guide.pdf* (Gargi Bhardwaj). The
three generators (`dotify.py`, `radar.py`, `cards.py`) and the three workflows
are hers; the photo, the words, the skill numbers and the project list are mine.

---

## What regenerates itself

| workflow | produces | schedule |
|---|---|---|
| **Metrics** (`metrics.yml`) | 3D isometric calendar, language mix, achievements → `assets/metrics.*.svg` | every 6h |
| **Snake** (`snake.yml`) | snake eating the contribution graph → `output` branch | every 12h |
| **Charts and cards** (`radar.yml`) | both radars + stat card + project cards → `assets/radar*.svg`, `assets/card-*.svg` | daily 03:30 |

The **portrait is local-only** — no workflow touches it. Regenerate it by hand
when the photo changes (below).

---

## 1. The portrait (local, one-time)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install pillow rembg

python scripts\prep_photo.py photo.jpeg
python scripts\dotify.py me-cutout.png -o assets\portrait --cols 100 --equalize --detail 0.5 --color --bg "#0d1117" --reveal
```

- `prep_photo.py` cuts the background out of `photo.jpeg` (busy tiled wall) and
  crops to a head-and-shoulders square → `me-cutout.png`. First run downloads a
  ~5 MB model. `rembg` is only needed for this step.
- `--color --bg "#0d1117"` — colour dots on an opaque dark panel. Straight
  `--color` (no panel) is what the guide ships, but a white shirt on GitHub's
  light theme disappears without the panel, so this one carries its own.
- `--equalize` is the flag that matters: it buys back shadow detail a lit face
  against dark hair would otherwise lose. `--detail 0.5` puts facial structure
  back on top.
- `photo.jpeg` / `me-cutout.png` are gitignored — the committed artefact is
  `assets/portrait.svg`.

## 2. The radars and cards (local preview)

```powershell
pip install pillow
python scripts\radar.py --data assets\skills.json -o assets\radar
python scripts\radar.py --github animesh8787 -o assets\radar-langs --limit 7 --values --curve 0.4 --exclude "html,scss,shell,makefile,dockerfile,batchfile,procfile,mako,tex"
$env:GITHUB_TOKEN = (gh auth token)   # optional — 6 stat tiles instead of 3
python scripts\cards.py --user animesh8787 --out assets
```

The **Charts and cards** workflow runs exactly these on GitHub every day, so
committing the generated SVGs is optional — but doing it means the profile isn't
full of broken images between the first push and the first workflow run.

Open `preview.html` (via a local server, e.g. `python -m http.server`) to see
every asset on a dark and a light card before pushing.

## 3. Push

Create `animesh8787/animesh8787` on GitHub — **public**, and **do not** tick
"Add a README file" (keeps the push clean).

```bash
git push -u origin main
```

`origin` is already set to `https://github.com/animesh8787/animesh8787.git`.

## 4. Let Actions write to the repo

Repo → **Settings → Actions → General → Workflow permissions** →
**Read and write permissions** → Save.

Without this the Snake workflow can't create the `output` branch and the
Charts-and-cards workflow fails at `git push`.

## 5. Add the metrics token

`lowlighter/metrics` reads profile-level data the built-in `GITHUB_TOKEN` can't see.

1. <https://github.com/settings/tokens> → **Generate new token (classic)** — not fine-grained.
2. Scope: **`read:user`** (add **`repo`** if you want private contributions counted).
3. Repo → **Settings → Secrets and variables → Actions → New repository secret**,
   name it **`METRICS_TOKEN`** exactly, paste the value.

## 6. Kick off the workflows

Repo → **Actions** tab → enable workflows if prompted → **Run workflow** on each
of the three. First runs take a couple of minutes (Metrics is the slowest).

The snake URLs in the README 404 until the Snake workflow has finished once —
that's expected, the `output` branch doesn't exist yet.

---

## Editing later

| change this | then | who redraws |
|---|---|---|
| the photo | re-run steps 1 | you, locally |
| `assets/skills.json` (self-rated radar) | push | Charts-and-cards workflow |
| `assets/projects.json` (featured repos) | push | Charts-and-cards workflow |
| the words / layout | edit `README.md` | nobody, it's just markdown |
| timezone for the "commits by hour" chart | `config_timezone` in `metrics.yml` | Metrics workflow |

### Notes on the current content

- **`skills.json`** values are a first guess from the repo languages — they're
  self-rated 0–100, edit them until they're honest.
- **`projects.json`** — two of the four repos have no GitHub description; the
  overrides here fill that in, but setting real descriptions on the repos
  themselves is worth doing (and then the overrides can go).
- **`README.md`** still has the terminal-prompt section headers from the guide.
  Keep them or don't — the mechanism (self-drawing SVGs) is the reusable part.
