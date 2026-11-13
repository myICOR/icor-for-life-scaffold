# Databases

The data shelf. Real SQLite databases live here, next to your notes: an
Apple Health archive, an analytics store, a log your own automation
writes. Notes are for knowledge; millions of rows are data, and data
wants SQL. This room ships empty on purpose - whatever lands here is
yours.

## What belongs here, and what does not

One test decides it: **does anything in this vault regenerate this
database?**

- **No** - it is a source. It belongs here, and losing the file loses
  real data. Back it up the way you back up your notes.
- **Yes** - it is a copy of your notes, and it does not belong here.
  Obsidian's own search and Bases query the notes directly; a database
  built from them is just a second copy that goes stale. (An early
  version of this scaffold kept such a mirror and retired it for
  exactly that reason.)

Databases can be large, so this room is a good candidate for your
backup tool and a poor one for git.

## The plugin that opens this room

The **ICOR for Life - SQLite Viewer** plugin (not in Obsidian's community
directory yet; the root `README.md`, "Install the ICOR for Life plugins",
says how to install it) opens any `.db`, `.sqlite` or
`.sqlite3` file in the vault, and this room is its home:

- **Browse.** Click a database and see every table with its row count,
  the schema, and the data page by page, with sorting and per-column
  filters.
- **Query.** A console for your own read-only SQL, with a "Copy as
  CSV" button.
- **Dashboards, no SQL needed.** Build charts and stat tiles from your
  data through a plain-words form; the dashboards are small JSON files
  the plugin keeps in a subfolder here.
- **Every device.** Small databases open live on phone and tablet too.
  A database too big for the phone stays on the desktop; the desktop
  computes the dashboards, caches the results in this room, and the
  phone shows the same dashboards from that synced cache.
- **Read, never write.** The plugin opens every database read-only and
  refuses every writing statement, so browsing and querying can never
  change your data.

## Getting databases in

Drop a `.db` file here, or point your own tools and automations at
this folder - a health export script, an engagement log, anything that
writes SQLite. If databases already sit elsewhere in your vault, the
plugin's settings carry a tidy-up button that lists them and moves
them into this room after you confirm.
