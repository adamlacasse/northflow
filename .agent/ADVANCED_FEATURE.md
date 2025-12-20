# NorthFlow – Advanced Feature Requirement

## Requirement Summary

NorthFlow must include **at least one advanced database feature** that demonstrates meaningful data aggregation or summarization beyond basic CRUD operations.

This requirement is satisfied by implementing **one (or more)** of the following at the database level:

- A **VIEW**
- A **STORED PROCEDURE**

The feature must:

- Read from multiple tables
- Use at least one **aggregate function**
- Produce **user-friendly, summarized output**
- Demonstrate real analytical or reporting value

---

## Chosen Implementation Strategy (NorthFlow)

NorthFlow implements a **read-focused analytical feature** that summarizes user mindfulness activity over time.

### Core Concept

Aggregate **check-in data** to provide insight into:

- Frequency of check-ins
- Average mood/score
- Time-based trends (daily summaries)

This aligns with the app’s purpose: *mindfulness, reflection, and habit tracking*.

---

## Advanced Feature: Daily User Summary

### Type

**SQL VIEW**

### Description

Provides a per-user, per-day summary of mindfulness check-ins and scored answers.

### Tables Involved

- `users`
- `checkins`
- `answers`

### Aggregates Used

- `COUNT(DISTINCT ...)` — number of check-ins per day
- `COUNT(...)` — number of answers captured
- `AVG()` / `MIN()` / `MAX()` — summary stats over `answers.score`

---

## Implemented View Definition (`user_daily_summary`)

```sql
CREATE VIEW user_daily_summary AS
SELECT
    u.id AS user_id,
    u.first_name,
    u.last_name,
    DATE(c.checkin_time) AS checkin_date,
    COUNT(DISTINCT c.id) AS total_checkins,
    COUNT(a.question_id) AS total_answers,
    AVG(a.score) AS avg_score,
    MIN(a.score) AS min_score,
    MAX(a.score) AS max_score
FROM users u
LEFT JOIN checkins c ON c.user_id = u.id
LEFT JOIN answers a ON a.checkin_id = c.id
GROUP BY
    u.id,
    u.first_name,
    u.last_name,
    DATE(c.checkin_time);
