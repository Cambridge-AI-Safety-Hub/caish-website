# caish.org

This is the website of the Cambridge AI Safety Hub (CAISH). It is plain HTML and CSS with no framework, so every page is one file you can open and edit. Cloudflare publishes it automatically whenever `main` changes.

## Who looks after it

- Maintainer: _to be decided_. Reviews and merges pull requests, keeps this README current and owns the design.
- Backup: _to be decided_. Merges urgent fixes when the maintainer is away.
- Design: see [docs/design.md](docs/design.md) for how the site should look and read.

Anyone in CAISH can suggest a change. Changes go live only when the maintainer merges them.

## Making a change

Every change goes through a pull request. Nobody pushes to `main` directly.

1. Make the change on a new branch (one of the three ways below).
2. Open a pull request. Cloudflare builds a preview of it and posts the link on the pull request.
3. Check the preview on your phone and laptop.
4. Ask the maintainer to review. When they merge it, caish.org updates within a minute or two.

**With Claude on the web.** This is the easiest route and needs no installation. Go to [claude.ai/code](https://claude.ai/code), connect your GitHub account, pick this repository and describe the change in plain words (for example "add Jane Doe to the committee on the About page, photo attached"). Claude reads [CLAUDE.md](CLAUDE.md), makes the edit on a branch and opens the pull request. Then follow steps 2 to 4.

**With Claude Code on your laptop.** Clone the repository, run `claude` inside the folder and describe the change. Ask it to open a pull request when it is done. You can check the result before pushing with `npx wrangler dev`, which serves the site at http://localhost:8787.

**By hand on GitHub.** For a typo, open the file on github.com, click the pencil icon, edit and choose "Create a new branch and start a pull request".

## What is where

| Path | What it is |
|---|---|
| `*.html` at the top level | One file per page. `about.html` is served at caish.org/about. |
| `styles.css` | Shared styles used by almost every page. Many pages also have their own `<style>` block at the top. |
| `fellowship.css`, `desk.css` | Extra styles for those two pages. |
| `enhancements.js` | Small visual touches shared by all pages (mobile menu, fade-ins, link underlines). |
| `sw.js` | Service worker that makes repeat visits load faster. |
| `images/` | All photos and logos. |
| `videos/` | Short hover clips only. Full videos live in Cloudflare R2 (see Hosting). |
| `course/verification/` | The AI Workload Verification reading course, with sign-in and saved progress. |
| `hardware/` | HAP sub-pages: `schedule/` (unlisted) and `feedback/` (course feedback form). |
| `participants/` | HAP 2026 participant directory (unlisted, built by `tools/participants/`). |
| `roles/` | Job descriptions linked from /hiring. |
| `data/fellows.json` | Certificate records shown at caish.org/verify/&lt;ID&gt;. |
| `functions/` | Small server functions served at `/api/<name>` (see below). |
| `worker/index.js` | Connects the server functions to Cloudflare. Rarely needs changing. |
| `_redirects` | Short links and old addresses (/talk, /eoi, /careers and so on). |
| `_headers` | Security and caching headers. |
| `wrangler.jsonc` | Cloudflare settings. |
| `cache-bust.sh` | Runs on every deploy and stamps CSS and JS links with a version so browsers fetch new files. |
| `tools/` | Scripts that are run by hand, never published. |
| `docs/` | Notes for maintainers, never published. `docs/archive/` keeps old versions of pages that matter (such as the July 2026 operations job advert). |
| `netlify.toml` | Settings from the old Netlify hosting. Delete once Netlify is closed. |

The navigation bar and footer are copied into every page. To add a menu item, change it in each page (Claude can do this in one go).

### Pages

- Main: home (`index`), about, hiring, privacy, terms.
- Programmes: fellowship, policy, desk, mars, research (MARS publications), hardware (HAP), course/verification.
- Unlisted: apply (Fellowship or Desk chooser, shared directly), course (HAP 2026 pre-work), feedback, events (live Luma list), video, hannes, cam, puria, hardware/schedule, participants, verify.
- Small forwarding pages: alignmentfellowship, mail (newsletter sign-up), mars-apply, hardware-eoi, mentor, hdwsa, social, lunch.

### Server functions

These run on Cloudflare and keep API keys off the public site.

| Address | What it does | Needs |
|---|---|---|
| `/api/events` | Lists upcoming CAISH events from Luma for events.html | `LUMA_API_KEY` |
| `/api/hdwsa` | Sends visitors (via caish.org/hdwsa) to the next How Do We Solve Alignment event | `LUMA_API_KEY` |
| `/api/social` | Sends visitors (via caish.org/social) to the next social | `LUMA_API_KEY` |
| `/api/lunches` | Sends visitors (via caish.org/lunch) to the next lunch | `LUMA_API_KEY` |
| `/api/feedback` | Saves course feedback into the HAP Airtable base | `AIRTABLE_SKETCH_TOKEN` |
| `/api/sketch` | Saves project sketches from the verification course into the HAP Airtable base | `AIRTABLE_SKETCH_TOKEN` |

`LUMA_EXTRA_EVENT_IDS` (optional) is a comma-separated list of Luma event IDs to include even if they are not on the CAISH calendar.

## Common tasks

- Text: find the page file and edit the words. Search the repository for a phrase if you are unsure which file it is in.
- People: put the photo in `images/` with a lowercase, hyphenated name (`jane-doe.jpg`), under 500 KB and at most 1200 px wide. Copy an existing person's card in the page and change it.
- Certificates: add an entry to `data/fellows.json` following the existing ones. The certificate link is caish.org/verify/&lt;ID&gt;.
- Talk: point caish.org/talk at the new term's Luma event by changing the `/talk` line in `_redirects`.
- HAP: the next-edition checklist is in a comment at the top of `hardware.html`.
- Videos: upload the file to the R2 bucket and link it by its r2.dev address. The bucket address is allowed in the `Content-Security-Policy` line of `_headers`.
- Participants: `AIRTABLE_TOKEN=... python3 tools/participants/build.py` rebuilds the directory from Airtable. It only includes people who gave website consent. Andrea Caforio declined, so never add him by hand.
- Roles: the wording on `roles/*.html` is the public record for visa sponsorship. Change markup if needed, but leave the words alone unless a director says otherwise.

## Hosting

- Cloudflare: the site is a Worker called `caish-website` on the CAISH Cloudflare account (login ops@caish.org, in the Core vault in 1Password). Cloudflare also holds the caish.org domain and DNS.
- Deploys: Cloudflare watches this repository. A merge to `main` builds and publishes the site. Every other branch gets a preview link. The build runs `bash cache-bust.sh`, then `npx wrangler deploy`.
- Secrets: `LUMA_API_KEY`, `AIRTABLE_SKETCH_TOKEN` and `LUMA_EXTRA_EVENT_IDS` are set under Workers & Pages > caish-website > Settings > Variables and secrets. Copies are in 1Password (Core vault). They never go in the repository.
- Videos: the full-length videos are in the Cloudflare R2 bucket `caish-videos`, served from `pub-fd3e7e854dc549da85f015f509d5ec9a.r2.dev`.
- Course sign-in: the verification course uses a Supabase project (`joggzpdemdmyvnlhtjte`) for logins and saved progress. The key in `course/verification/supabase-config.js` is public by design.
- Logs: Workers & Pages > caish-website > Logs shows errors from the server functions.

Which person owns which account is recorded in the CAISH systems and access doc.

## Known issues

- `images/og-image.png` (the link-preview image for 12 pages) does not exist, so those pages show no image when shared.
- About 130 images in `images/` are no longer used by any page.
- verify.html says "Alignment Fellowship Certificate" in its title even for HAP certificates.
- `course/verification/4.html` asks people to share documents with gaurav@caish.org.
- The R2 video bucket (`caish-videos`) is on Gaurav's personal Cloudflare account and needs moving to the CAISH one, which changes the video addresses in hannes.html, cam.html, puria.html, hardware.html and `_headers`.
- The Supabase project for course sign-in needs an ops@ owner.
