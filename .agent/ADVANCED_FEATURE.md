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

## Example Advanced Feature: Daily User Check-In Summary

### Type

**SQL VIEW** (preferred for simplicity and readability)

### Description

Provides a per-user, per-day summary of mindfulness check-ins.

### Tables Involved

- `users`
- `checkins`
- `answers` (optional, depending on implementation)
- `user_questions` (optional context)

### Aggregates Used

- `COUNT(*)` — number of check-ins per day
- `AVG(score)` — average mood or rating
- `MIN()` / `MAX()` — first and last check-in times (optional)

---

## Example View Definition

```sql
CREATE VIEW daily_user_checkin_summary AS
SELECT
    u.id AS user_id,
    CONCAT(u.first_name, ' ', u.last_name) AS user_name,
    DATE(c.checkin_time) AS checkin_date,
    COUNT(c.id) AS total_checkins,
    AVG(a.numeric_value) AS avg_mood_score
FROM users u
JOIN checkins c ON c.user_id = u.id
LEFT JOIN answers a ON a.checkin_id = c.id
GROUP BY
    u.id,
    DATE(c.checkin_time);
