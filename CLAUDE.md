# Instructions for Claude

You are editing caish.org, the website of the Cambridge AI Safety Hub. Read README.md for how the site is put together and docs/design.md for how it should look and read. The person asking for a change is usually a CAISH team or committee member, often without a coding background, so explain what you did in plain words.

## Workflow

- Work on a new branch named after the change (`update-committee`, `fix-mars-dates`). Never commit to `main`.
- Keep each pull request to one change. Write the title and description so a non-technical reviewer can follow them, and say which pages changed.
- Before opening the pull request, run `npx wrangler dev` and load each page you touched at http://localhost:8787. Check that it renders, that links work and that the layout holds at phone width (around 375 px).
- Tell the person to check the preview link Cloudflare posts on the pull request, and that the maintainer named in README.md merges it.

## How the site is built

- Plain HTML, CSS and a little JavaScript. Do not add a framework, a package manager, a build tool or a CSS library.
- Reuse the classes in `styles.css` and the patterns on similar pages before writing new CSS. Page-specific styles go in that page's own `<style>` block.
- The nav and footer are copied into every page. A change to either must be made in every HTML file that has them.
- New pages: copy the closest existing page, update the `<title>`, description and Open Graph tags, and keep the `styles.css?v=` and `enhancements.js?v=` links (the deploy stamps the version).
- Short links and moved pages go in `_redirects`. Headers, including the Content-Security-Policy, go in `_headers`. If a page needs a new outside service (a form, an embed, a video host), add it to the policy there or it will be blocked.
- Images go in `images/` with lowercase hyphenated names. Compress them first (under 500 KB, at most 1200 px wide). Always set `alt` text and `width`/`height`.
- Never put API keys or tokens in the repository. Server-side secrets live in Cloudflare (see README.md, Hosting).

## Writing

- UK English (programme, organise, centre, colour).
- No em dashes. Use commas, brackets or a full stop.
- No semicolons.
- Keep copy plain and specific. Avoid marketing phrasing, rhetorical contrasts ("not X, but Y") and punchy one-line closers.
- Describe CAISH as fiscally sponsored by Meridian Impact CIC, never as run by Meridian or a project of it.

## Things to leave alone

- The wording on `roles/*.html` is the record used for visa sponsorship. Change markup only, unless a director says otherwise.
- `docs/archive/` holds old page versions on purpose.
- The participant directory (`participants/`) only lists people who consented. Rebuild it with `tools/participants/build.py` and never add someone by hand. Andrea Caforio declined consent.
- Unlisted pages (participants, hardware/schedule, feedback) stay out of the nav and keep their noindex settings.
