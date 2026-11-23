# ICOR for Life security policy

ICOR for Life is a content folder: the folders, the note templates, the concept Guidelines and the Obsidian setup. It is mostly markdown, and markdown doesn't attack anybody. The parts that run are the parts this policy is about: the life scripts, the Obsidian settings in the zip, and the release pipeline that builds that zip. Since 2.3.0 the zip carries no plugin, no theme and no myPKA file.

The AI team is not part of ICOR for Life. Agent teams come from myPKA 8, a separate download in its own folder; a myPKA 7 folder that also holds ICOR for Life keeps its team files under myPKA's policy. The contracts, the team scripts, the hooks and the write guard they run, the updater, the resolver, `add-mcp-server.py`, the expansion-pack installer and the shipped `.mcp.json` all belong to myPKA, which has its own policy: [SECURITY-myPKA.md](https://github.com/myICOR/myPKA/blob/main/SECURITY-myPKA.md).

## The key rule: ICOR for Life never ships or needs a secret

- **No release carries a key, token or password.** Nothing in this repository does either. The release workflow uses only the short-lived token GitHub gives each run, and only on the steps that talk to GitHub.
- **ICOR for Life needs no account and no key to run.** The life scripts open no network connection. They read and write notes in your folder. The only outside program one of them starts is Obsidian, when `open-in-obsidian.py` opens a note for you.
- **ICOR for Life ships no `.env`, no `.mcp.json` and no hook.** If your folder has them, they came from myPKA or from you.
- **Plugin settings stay yours.** Some plugins keep a token or a key in their own `data.json` (Planner, Connect, Scaffold Check, Terminal). The zip carries only each plugin's `main.js`, `manifest.json` and `styles.css`, and the theme's `manifest.json` and `theme.css`. A `data.json` is never in a zip, and an update never brings one.
- **Never paste a key into a report or a chat.** We never ask you to.

Found a real secret in an ICOR for Life release, in this repository or in its history? That's the most serious report we can get. Send it at once (below).

## Supported versions

| Version | Security fixes |
| --- | --- |
| 2.x | Yes. Fixes ship as a new 2.x release. |
| 1.34.1 and earlier (the Scaffold before the split into ICOR for Life and myPKA) | No. Move to 2.x together with myPKA 6.x: [README-myPKA.md](https://github.com/myICOR/myPKA/blob/main/README-myPKA.md), "Coming from ICOR for Life 1.34 or earlier". |

A fix always ships as a new version. A published zip is never replaced or patched in place. To get a fix, download the new release and check it (below). The **ICOR for Life - Scaffold Check** plugin then shows what is missing, what changed and which files a version removed. It only reads and reports; you make the changes. Only the newest 2.x release gets fixes, so stay on it.

## How to report a problem

**Never in a public issue.** Use GitHub's private vulnerability reporting on this repository:

https://github.com/myICOR/icor-for-life-scaffold/security/advisories/new

Only you and the maintainers see the report until a fix ships. You need a GitHub account. Without one, write to `support@myicor.com` with `SECURITY` and `icor-for-life` in the subject.

How we handle personal data in reports: https://myicor.com/privacy#github

Not sure whether it's ICOR for Life, myPKA or a plugin? Report it here. We move it to the right place and tell you.

A useful report has:

- **The version**, from `.icor-for-life/VERSION`. Please don't guess it from the download date.
- **Your operating system, your Python version** (`python3 --version`) **and your Obsidian version.** For a plugin or the theme, its version too.
- **The file and the line.** Name the script under `Scripts/`, or the file under `.obsidian/`, and the line number, not only the behaviour.
- **Steps to reproduce on a throwaway copy.** Copy the folder to a scratch place and break that one. Never test against notes you care about, and never send us your notes.
- **A harmless proof.** A payload that writes a file named after the finding proves as much as one that deletes a folder, and costs nobody anything.
- **No real credentials.** Never paste a token, a line from your `.env` or a plugin's `data.json`. Describe the credential instead ("the token my Connect plugin uses"). If one of your keys was exposed, rotate it with its provider first, then report.

## What's in scope

**The life scripts** under `06 AI Team/AI Team Knowledge/Scripts/`: `life-snapshot.py`, `check-quality.py`, `check-bases.py`, `find-entity.py`, `new-entity.py`, `new-journal-entry.py`, `new-base.py`, `set-property.py`, `planner-week.py`, `link-dates-to-daily-notes.py`, `stamp-processed.py`, `open-in-obsidian.py`, `validate-scaffold.py` and their test suites. Any script that writes outside the path it was given or outside your folder, or follows a symbolic link out of it. Any script that runs a string built from note content or a file name, starts a program other than the one it names, loads code from a folder your notes can reach, or opens a network connection. Any script that puts a secret or a private note into a tracked file, a log line, an error message or your terminal. `noteio-icor.py` began as a copy of myPKA's `noteio.py` and is ICOR for Life's own since 2.3.0: report it here.

**The shipped Obsidian setup** (`.obsidian/`). Any setting in the zip that turns on something you didn't choose, loads a plugin, theme or snippet that isn't ours, or carries leftover state from our machines (a `data.json`, a token, a workspace).

**No bundled plugins or theme.** Since 2.3.0 the zip carries no plugin and no theme, and its `community-plugins.json` enables none: you install the ICOR for Life plugins and the INKLINE theme from Obsidian's community directory. In scope here: a zip that carries a plugin or theme folder, or enables a plugin. A bug in the plugin or theme code itself goes to its repository (below).

**The release workflow** (`.github/workflows/release.yml`). Any way to get a release out without every gate passing, to build it from anything but its tag, to replace a published file, or to reach the workflow's token.

**The attestations and the zip.** A zip or a `manifest.json` that passes the check below without being built by `release.yml` from its tag on a GitHub-hosted runner. A zip that carries anything not in that tag: build tooling, personal data, a repository-only file, a plugin, a theme or any secret.

## What's out of scope

These aren't vulnerabilities in ICOR for Life, and we close them as such:

- **The AI team: report to myPKA.** The write guard, the hooks, `session-start.py`, the updater, the resolver, `add-mcp-server.py`, `scaffold-init.py`, the expansion-pack installer and the shipped `.mcp.json` are myPKA's. Its policy: [SECURITY-myPKA.md](https://github.com/myICOR/myPKA/blob/main/SECURITY-myPKA.md). Its form: https://github.com/myICOR/myPKA/security/advisories/new.
- **Plugin and theme code.** You install them from Obsidian's community directory. Each has its own repository and its own `SECURITY.md`:
  [Planner](https://github.com/myICOR/icor-for-life-planner),
  [Focus](https://github.com/myICOR/icor-for-life-focus),
  [Connect](https://github.com/myICOR/icor-for-life-connect),
  [AI Chat](https://github.com/myICOR/icor-for-life-chat),
  [Interface](https://github.com/myICOR/icor-for-life-interface),
  [Scaffold Check](https://github.com/myICOR/icor-for-life-scaffold-check),
  [SQLite Viewer](https://github.com/myICOR/icor-for-life-sqlite-viewer),
  [Terminal](https://github.com/myICOR/icor-for-life-terminal),
  [Outliner](https://github.com/myICOR/icor-for-life-outliner),
  [PDF Annotation](https://github.com/myICOR/icor-for-life-pdf-annotation),
  [Canvases](https://github.com/myICOR/icor-for-life-canvases),
  [Scratchpad](https://github.com/myICOR/icor-for-life-scratchpad),
  [INKLINE theme](https://github.com/myICOR/icor-for-life-inkline).
- **Obsidian itself.** Report to [Obsidian](https://github.com/obsidianmd/obsidian-releases/issues).
- **Your AI host and its model.** ICOR for Life is not a sandbox and can't stop a model you gave file access from using it.
- **Your own notes, keys and setup.** What you put in your folder, a plugin's settings, where you sync it and who uses your computer. Anything in ICOR for Life that moves a key or a note out of your folder, or into a file you didn't choose, is in scope.
- **The myICOR web app and its MCP endpoint.** That is a hosted service, not code in this repository. Still use the private form above, say it's about the hosted service, and we pass it to the right people.
- **Problems in Python, git, Obsidian's own code or your operating system.** Report those to their makers. How ICOR for Life calls them is in scope.
- **Hardening with no shown impact.** "The scripts aren't signed", "`data.json` isn't encrypted", scanner output with no working proof.
- **Social engineering, physical access, or attacks that need you to already be running the attacker's code.**

## Check that a download is genuine

Every release zip, and the `manifest.json` beside it, carries a build-provenance attestation: a signed record of which workflow built these exact bytes, from which tag. Check it with the GitHub CLI (`gh`) before you unpack the zip. Put your version in place of `<version>`, as one line:

```
gh attestation verify icor-for-life-obsidian-edition-<version>.zip --repo myICOR/icor-for-life-scaffold --signer-workflow myICOR/icor-for-life-scaffold/.github/workflows/release.yml --source-ref refs/tags/<version> --deny-self-hosted-runners
```

Use the download only if it prints that verification succeeded. The unversioned `icor-for-life-obsidian-edition.zip` is the same bytes and checks with the same command.

Releases up to and including 2.0.0 were built before the repository moved from `TomSolid` to `myICOR`, so their record carries the old name. Check them with `--owner TomSolid` in place of `--repo ...` and `--signer-workflow TomSolid/icor-for-life-scaffold/.github/workflows/release.yml`.

This proves who built the zip: our release workflow, from that tag, on a GitHub-hosted runner. It doesn't prove the code is free of bugs. That's what this policy is for.

## Our timelines

ICOR for Life is maintained by a small team. We read every report, and we reply when we can. We can't promise a time to reply or a time to ship a fix, and nothing in this policy is a deadline we owe you.

Please keep your finding private until a fix ships, or until 90 days after your report, whichever comes first. If we need more time, we may ask you. Waiting longer is your choice.

When the fix ships, we publish a GitHub security advisory on this repository and name the fix in `.icor-for-life/CHANGELOG.md`. We credit you by name and link in both, unless you'd rather stay anonymous. If a problem is being used against members before a fix exists, we may publish a warning and a safe workaround earlier, and we tell you first.

There's no bug bounty. We can't pay for reports.

## Good-faith research

If you research ICOR for Life in good faith and follow this policy, Paperless Movement S.L., the company behind ICOR for Life, authorizes that research in advance. For that research we won't file a criminal complaint against you (a denuncia or querella in Spain, a Strafantrag in Germany) and we won't bring a civil claim against you.

That holds when you:

- Test only what "What's in scope" lists, on a copy of ICOR for Life on your own computer, or in your own fork or throwaway repository.
- Test the release workflows in your own fork. Don't open a pull request meant to run code in our repository.
- Stop at the first harmless proof. Don't use a finding to reach further, and don't keep any access you gained.
- Don't access, copy, keep, change or destroy data that isn't yours. If you see someone else's data by accident, stop, delete what you have and tell us in your report.
- Don't slow down or break anything for anyone else: no denial of service, no load testing, no spam, no social engineering, no physical access.
- Report only through one of the private channels above, or privately through INCIBE-CERT, Spain's national cybersecurity response team, and keep the finding private for the time set in "Our timelines".

Where it ends:

- **It doesn't cover the myICOR web app, its MCP endpoint or any other hosted service.** Don't test them. If you notice a problem there in normal use, please tell us through the form. Probing the service is not authorized.
- **It binds only Paperless Movement S.L.** We can't give up the rights of anyone else, such as GitHub, other users or the makers of tools you connect. We can't bind a prosecutor or a court in any country. In Spain, for example, a prosecutor can act without our complaint when many people are affected.
- If someone else takes action against you over research that followed this policy, we'll confirm in writing, on request, that we authorized it.
- If your report shows a vulnerability that is being actively exploited, EU law may require us to notify the EU cybersecurity authorities (ENISA and the national response team). We'll tell you when we do, and we won't share your name without your consent unless the law requires it.

Not sure something is allowed? Ask us through the form before you test.

Thank you. A report that arrives privately, from a scratch copy, with the line quoted and nothing real broken, is worth a great deal.
