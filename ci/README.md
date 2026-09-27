# Activating CI and the website (one-time, ~2 minutes)

The two GitHub Actions workflows live here because the automation that prepared this repo isn't allowed to
write to `.github/workflows/` (GitHub requires a special `workflows` permission for that). Moving them into
place is a one-time step with your own account:

| File | What it does |
|---|---|
| [`workflows/ci.yml`](workflows/ci.yml) | Runs the test suite on every push/PR: Linux, Windows, macOS, Python 3.10–3.13, plus the slow Excel/notebook checks and a generated-files drift check |
| [`workflows/pages.yml`](workflows/pages.yml) | Builds the MkDocs site (with the SQL Playground and flashcards) and deploys it to GitHub Pages on every push to `main` |

## Option A: on your computer

```bash
git checkout main && git pull
mkdir -p .github && git mv ci/workflows .github/workflows
git commit -m "Activate CI and Pages workflows" && git push
```

## Option B: in the browser (no git needed)

1. On GitHub, open `ci/workflows/ci.yml` → **Raw** → copy everything.
2. Go to the repo home → **Add file ▸ Create new file** → name it `.github/workflows/ci.yml` → paste → **Commit**.
3. Repeat for `pages.yml`.

## Then turn on Pages

**Settings ▸ Pages ▸ Build and deployment ▸ Source: _GitHub Actions_**. The next push to `main` (or
**Actions ▸ Deploy site to GitHub Pages ▸ Run workflow**) publishes the site at
`https://<your-username>.github.io/JOBPREP_DA/`.

The README badges start working as soon as the workflows have run once.
