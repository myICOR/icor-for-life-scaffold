# Readwise

Your highlights from Readwise (books, articles, podcasts, posts) can sync straight into the Outer World.

1. Install the **Readwise Official** plugin from Obsidian's community directory and connect your account.
2. In its settings, set the folder to `06 Outer World/Readwise`.
3. On readwise.io/export/obsidian/preferences, turn on **YAML front matter** and paste:

```
type: source
source_type: {% if category == "books" %}book{% elif category == "articles" %}article{% elif category == "podcasts" %}podcast{% elif category == "tweets" %}post{% else %}other{% endif %}
author: "{{author}}"
source_url: {{url}}
consumed: true
projects: []
key_elements: []
topics: []
```

Every synced book or article then arrives as a source, ready to link to what it serves.
