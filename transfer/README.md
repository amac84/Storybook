# Transfer: Cove & Mars studio → amac84/Storybook

This folder packages the full studio built in Cloud Agent
`bc-01a06f84-d060-7233-a2b0-38c51702b801`.

That agent **cannot push to GitHub** (no write credentials on an
unlinked mobile-started VM). Apply this package from a Storybook
workspace that *can* push (e.g. Colvin Morris / Cursor opened on
`amac84/Storybook`).

## Contents

| file | purpose |
| --- | --- |
| `storybook-studio.tar.gz` | Full tree at commit `981fefe` (no `.git`) |
| `storybook-studio.bundle` | Git bundle of the whole branch history |
| `FILE_LIST.txt` | Paths included |

Branch name used here: `cursor/childrens-book-studio-b801`

## Option A — Tar extract (simplest)

In the **Storybook** clone (Colvin Morris workspace):

```bash
cd /path/to/Storybook
# copy storybook-studio.tar.gz into this repo first, then:
git checkout -b cursor/childrens-book-studio-b801
tar -xzf storybook-studio.tar.gz
git add -A
git status
git commit -m "Import Cove and Mars children's book studio from cloud agent"
git push -u origin cursor/childrens-book-studio-b801
```

Then open a PR into `main` if you want.

## Option B — Git bundle (keeps commit history)

```bash
cd /path/to/Storybook
git fetch storybook-studio.bundle cursor/childrens-book-studio-b801:cursor/childrens-book-studio-b801
git checkout cursor/childrens-book-studio-b801
git push -u origin cursor/childrens-book-studio-b801
```

If fetch syntax fails:

```bash
git bundle verify storybook-studio.bundle
git clone storybook-studio.bundle studio-import
cd studio-import
git remote add origin https://github.com/amac84/Storybook.git
git push -u origin cursor/childrens-book-studio-b801
```

## Prompt to paste into the Storybook agent

```text
Import the Cove & Mars studio from transfer/storybook-studio.tar.gz
(or the bundle). Create branch cursor/childrens-book-studio-b801,
commit if needed, and push to origin. Then open a PR into main.
Do not rewrite the studio; just land the files.
```

## Why “Fetch cloud agent branch” failed

This agent’s branch was never on GitHub (`repoUrl` was null; pushes
got 403). Fetching `bc-01a06f84-…` cannot work until something
pushes the branch — which this package enables from the Storybook side.
