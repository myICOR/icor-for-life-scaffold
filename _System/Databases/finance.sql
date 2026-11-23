-- Finance.sqlite: your own money, kept on this computer, in 05 Databases. Optional: delete the file if you do not
-- keep your finances here. Amounts are whole cents (12.34 EUR is 1234; money out is negative), so sums never round.
-- Read it with ICOR for Life - SQLite Viewer or any SQLite tool; your AI reads it through SQL and never copies it into
-- notes. Made from this file by `python3 _System/Tools/new-database.py finance`.

CREATE TABLE about (key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO about (key, value) VALUES
  ('what', 'Your money: accounts, transactions, categories and budgets. Yours only, never in a note.'),
  ('schema', '1'),
  ('docs', '05 Databases/README.md');

CREATE TABLE accounts (
  id TEXT PRIMARY KEY,          -- a short name you pick: giro, savings, visa
  name TEXT NOT NULL,
  bank TEXT,
  kind TEXT NOT NULL DEFAULT 'checking' CHECK (kind IN ('checking', 'savings', 'credit', 'cash', 'investment', 'loan', 'other')),
  scope TEXT NOT NULL DEFAULT 'private' CHECK (scope IN ('private', 'business')),
  currency TEXT NOT NULL DEFAULT 'EUR',
  iban_masked TEXT,             -- the last digits only, never the full number
  opened_on TEXT,
  closed_on TEXT,
  note TEXT
);

CREATE TABLE categories (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  group_name TEXT,              -- Living, Getting around, Fun…
  kind TEXT NOT NULL CHECK (kind IN ('income', 'expense', 'transfer')),
  sort INTEGER NOT NULL DEFAULT 0
);
-- A starter set, yours to change: rename, add, delete.
INSERT INTO categories (id, name, group_name, kind, sort) VALUES
  ('salary', 'Salary', 'Income', 'income', 10),
  ('other-income', 'Other income', 'Income', 'income', 20),
  ('housing', 'Housing', 'Living', 'expense', 30),
  ('groceries', 'Groceries', 'Living', 'expense', 40),
  ('eating-out', 'Eating out', 'Living', 'expense', 50),
  ('health', 'Health', 'Living', 'expense', 60),
  ('insurance', 'Insurance', 'Living', 'expense', 70),
  ('transport', 'Transport', 'Getting around', 'expense', 80),
  ('subscriptions', 'Subscriptions', 'Fun', 'expense', 90),
  ('shopping', 'Shopping', 'Fun', 'expense', 100),
  ('travel', 'Travel', 'Fun', 'expense', 110),
  ('gifts', 'Gifts', 'Fun', 'expense', 120),
  ('other', 'Other', 'Other', 'expense', 130),
  ('transfer', 'Transfer between my accounts', 'Transfers', 'transfer', 140);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES accounts (id),
  booked_on TEXT NOT NULL,      -- YYYY-MM-DD
  amount_cents INTEGER NOT NULL,
  currency TEXT NOT NULL DEFAULT 'EUR',
  counterparty TEXT,
  purpose TEXT,
  category_id TEXT REFERENCES categories (id),
  note TEXT,
  import_ref TEXT UNIQUE        -- the bank's own id, so a second import adds nothing twice
);
CREATE INDEX transactions_by_day ON transactions (booked_on);
CREATE INDEX transactions_by_category ON transactions (category_id, booked_on);

CREATE TABLE budgets (
  id INTEGER PRIMARY KEY,
  category_id TEXT NOT NULL REFERENCES categories (id),
  month TEXT NOT NULL,          -- YYYY-MM
  amount_cents INTEGER NOT NULL,
  UNIQUE (category_id, month)
);

-- Sorts a transaction into a category when its counterparty or purpose contains the pattern (highest priority first).
CREATE TABLE rules (
  id INTEGER PRIMARY KEY,
  category_id TEXT NOT NULL REFERENCES categories (id),
  field TEXT NOT NULL CHECK (field IN ('counterparty', 'purpose')),
  pattern TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 0
);

-- Money in and out per month and category.
CREATE VIEW monthly AS
  SELECT substr(booked_on, 1, 7) AS month, category_id,
         SUM(CASE WHEN amount_cents > 0 THEN amount_cents ELSE 0 END) AS in_cents,
         SUM(CASE WHEN amount_cents < 0 THEN -amount_cents ELSE 0 END) AS out_cents,
         COUNT(*) AS n
  FROM transactions GROUP BY month, category_id;

-- Each budget beside what was spent that month.
CREATE VIEW budget_vs_actual AS
  SELECT b.month, b.category_id, b.amount_cents AS budget_cents,
         COALESCE((SELECT -SUM(t.amount_cents) FROM transactions t
                   WHERE t.category_id = b.category_id AND substr(t.booked_on, 1, 7) = b.month AND t.amount_cents < 0), 0) AS spent_cents
  FROM budgets b;
