# Sample / demo data

CattleVision AI ships with **DEMO DATA** so the dashboard, animal list, and
alerts can be shown without a cattle farm.

Demo records are created automatically the first time the backend starts
(`SEED_DEMO_DATA=true`). They are stored in SQLite with `is_demo = true` and
labelled **DEMO DATA** in the UI.

Demo data is **not** real YOLO output. Do not present it as live farm results
in a viva or report without saying it is sample data.

## What is seeded

- 12 animals (`Cow #01` … `Cow #12`)
- Activity / observation history
- Behavior records
- Three example alerts (Cow #04, Cow #07, Cow #12)
- One demo analysis session

## Optional real media for detection demos

Place your own cattle photos/videos in this folder for local testing, or
download a public-domain cow photograph and use **Image Analysis**.

Suggested test:

1. Use a clearly visible side-view photo of one or more cows.
2. Avoid heavy blur, extreme zoom, or images with no animals.
3. Confirm the model file exists in `../models/yolov8n.pt`.

## Included sample media

- `sample_cattle.jpg` — public cattle photograph for Image Analysis demos
- `sample_cattle.mp4` — short generated clip for Video Analysis demos

These files are real images/video for the detector. Dashboard herd statistics still use **DEMO DATA** unless you run analysis yourself.
