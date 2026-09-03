# Test Cases

| ID | Module | Input / action | Expected result |
| --- | --- | --- | --- |
| TC01 | Health | GET /api/health | 200, app name CattleVision AI, model_loaded true or false with message |
| TC02 | Model | No file in models/ | Detection endpoints return 503 and “AI model not found…” |
| TC03 | Image validation | Upload notes.txt | 400 unsupported type |
| TC04 | Image validation | Oversized file | 400 size error |
| TC05 | Image happy path | Clear cow photo + model present | Count ≥ 1, boxes drawn, processed JPEG downloadable |
| TC06 | Image negative | Landscape with no cattle | cattle_count 0, readable observation text |
| TC07 | Video job | Valid mp4 | Immediate job id; progress increases; status completed |
| TC08 | Video invalid | Corrupt file | Failed job or 400 cannot read video |
| TC09 | Tracking | Two non-overlapping cows | Distinct Cow #01 and Cow #02 while visible |
| TC10 | Behaviour | Fast centroid motion | Walking/moving |
| TC11 | Behaviour | Wide box, little motion | Resting/lying or low activity |
| TC12 | Risk bands | Scores 20, 50, 70, 90 | Normal, Monitor, Attention Required, High Attention |
| TC13 | Alerts | High inactivity on video | Alert message + recommendation; resolve sets resolved true |
| TC14 | Dashboard | Default GET | Demo animals visible, includes_demo_data true |
| TC15 | Dashboard | include_demo=false on empty real DB | Totals may be 0, no crash |
| TC16 | Live camera | Permission denied | UI message; app remains usable |
| TC17 | Animal detail | Open Cow #04 demo | History, risk, recommendation, DEMO DATA badge |
| TC18 | Media path | GET /api/media/processed/../x | Rejected invalid path |
| TC19 | API docs | Open /docs | All routes listed |
| TC20 | Regression | pytest -q | Unit/API tests pass without GPU |

Automated coverage lives in `backend/tests/test_api.py`. Detection happy-path cases are manual once `yolov8n.pt` is installed.
