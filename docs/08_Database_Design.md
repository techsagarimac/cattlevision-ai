# Database Design

Engine: SQLite via SQLAlchemy. Foreign keys are enabled with PRAGMA.

## animals

| Column | Type | Notes |
| --- | --- | --- |
| id | integer PK | |
| animal_identifier | string | e.g. Cow #04 |
| created_at | datetime | |
| is_demo | boolean | DEMO DATA flag |
| last_behavior | string | cached |
| last_risk_score | float | 0–100 |
| last_confidence | float | |
| last_seen_at | datetime | |
| source_session_id | FK sessions | nullable |
| notes | text | |

## observations

Per-frame or sampled records: timestamp, confidence, behavior, movement_score, risk_score, bbox (x,y,w,h), frame_index, notes, is_demo.

## behavior_records

Segment-level activity: behavior, started_at, ended_at, duration_seconds, movement_label.

## alerts

alert_type, severity, message, recommendation, risk_score, timestamp, resolved, is_demo, animal_id.

## analysis_sessions

file_name, analysis_type (`image` / `video` / `live` / `demo`), start/end, totals, status, original_path, processed_path, notes, error_message, average_activity, job_id.

## Relationships

Animal 1—* Observation, BehaviorRecord, Alert.  
AnalysisSession 1—* Animal (via source_session_id).

## Demo seeding

On first startup, twelve demo animals and three alerts are inserted if no demo animal exists. They remain filterable with `include_demo=false`.
