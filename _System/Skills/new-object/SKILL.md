---
name: new-object
description: Create one object in the ICOR for Life folder - a project, goal, key element, topic, habit, person, company, note, document, source or a type the person added - in the right folder, from its template, with its required fields filled and linked. Use when the person says "new project", "add a goal", "add Anna as a contact", "make a note about…".
---

# Create an object

Every note is an object of one `type`. `_System/schema.json` gives each type its folder, template, required
fields, allowed values (`values`) and the types its links point to (`links`). Read the type there first.

1. **One thing, one note**: `python3 _System/Tools/find-entity.py "<name>"`. If it exists, update it instead.
2. **Required links first**: a **project** needs its `goal` (make the goal first if none fits); a **note** needs at
   least one of `projects`, `key_elements`, `topics`; a **document** needs `source_file`, the file already in
   `05 Assets/Documents/`.
3. **Create it**:
   `python3 _System/Tools/new-entity.py <type> "<Title>" --link "[[<target>]]" --set <field>=<value>`
   (`python3 _System/Tools/new-entity.py --list` shows the types and their folders). It picks the folder and template, puts each
   link in the field the schema gives that pair, and refuses a value the schema does not allow.
4. **Name** it by its natural title: `Spain Holidays`, `Alex Rivera`, `Health`. Journal entries are the exception:
   use skill **write-journal-entry**.
5. **Keep My Life notes short**: what it is, why it matters, its status. Material about it lives in Notes and links
   to it.

   Do not `--set` a field the template already fills (a project starts as `status: active`); change it afterwards.

**Types the person added** (a tool, a recipe, a trip) work the same way; `--list` shows them. When the person wants a
kind that does not exist yet, point them to `@tool` (or New object type) in Obsidian. Add one yourself only when they
ask: an entry in `_System/schema.json` shaped like the others, `_System/Templates/<type>.md`, a `.base` in its
folder like the others, and a view for it in `Objects.base`.

Set or change one field later, by the note's path:
`python3 _System/Tools/set-property.py "04 Inner World/My Life/Projects/<Project>.md" <field> <value>` (it checks the schema).
