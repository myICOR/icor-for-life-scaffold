# 11 Databases

The tables of this folder: one for your objects, and two optional databases for data that does not belong in notes.

- `Objects.base`: every object in one table, and a view per type (Projects, People, Sources, the types you add). Each type's folder has its own `.base` with all of that type's fields. Part of the core.
- `Health.sqlite` and `Finance.sqlite`: your health data and your money, as SQLite databases on this computer. Both are optional and start empty. Open them with ICOR SQLite Viewer (a table, a query, a dashboard), or with any SQLite tool.

Your health and money stay in these files. No note copies them, and nothing sends them anywhere. Your AI reads them through SQL when you ask, and answers in its own words without pasting your numbers into a note.

## Health.sqlite

Made from `_System/Databases/health.sql`. Fill it from an Apple Health export, a scale or a watch, or by hand. Each table says what goes in it:

| Table | One row is |
| --- | --- |
| `health_metric` | one measurement: `metric_name` (snake_case: weight_body_mass, body_fat_percentage, resting_heart_rate, heart_rate_variability, vo2_max, step_count, sleep_hours…), `qty`, `unit`, `local_date` (YYYY-MM-DD), `recorded_at_utc`, `source` |
| `workouts` | one workout: `workout_type`, `start_time`, `end_time`, `duration_min`, `active_energy_kcal`, `distance_km`, `heart_rate_avg`, `heart_rate_max`, `source`, `note` |
| `medications` | one dose: `date`, `medication`, `dosage`, `unit`, `status` (taken, skipped) |
| `symptoms` | one symptom: `start_time`, `end_time`, `symptom`, `severity` (mild, moderate, severe), `source`, `note` |
| `mood_entries` | one mood: `timestamp`, `valence` (-1 to 1), `labels`, `associations`, `note` |
| `daily` (a view) | each measurement per day: average, lowest, highest |
| `about` | what the file is and its schema version |

`health_metric` has the shape ICOR for Life - Health Tracker reads, so the two fit once that plugin is out.

## Finance.sqlite

Made from `_System/Databases/finance.sql`. Amounts are whole cents (12.34 EUR is 1234; money out is negative), so sums never round. Fill it from your bank's CSV export or by hand.

| Table | One row is |
| --- | --- |
| `accounts` | one account: `id` (a short name you pick), `name`, `bank`, `kind` (checking, savings, credit, cash, investment, loan, other), `scope` (private, business), `currency`, `iban_masked` (the last digits only), `opened_on`, `closed_on`, `note` |
| `categories` | one category: `id`, `name`, `group_name`, `kind` (income, expense, transfer), `sort`. A starter set is in it, yours to change |
| `transactions` | one booking: `account_id`, `booked_on`, `amount_cents`, `currency`, `counterparty`, `purpose`, `category_id`, `note`, `import_ref` (the bank's own id, so a second import adds nothing twice) |
| `budgets` | one budget: `category_id`, `month` (YYYY-MM), `amount_cents` |
| `rules` | sorts a booking into a category when its `counterparty` or `purpose` contains `pattern` (highest `priority` first) |
| `monthly` (a view) | money in and out per month and category |
| `budget_vs_actual` (a view) | each budget beside what was spent that month |
| `about` | what the file is and its schema version |

## Not using one?

Delete the file: nothing else in the folder needs it. To have it back, empty: `python3 _System/Tools/new-database.py health` (or `finance`). Not using either? Turn off ICOR SQLite Viewer as well (see "What's core, what's optional" in README.md).
