# Project Abstract

CattleVision AI is an AI-based cattle health and welfare monitoring system developed as an undergraduate major project in computer science / information technology. The system applies object detection and lightweight video tracking to images and video of cattle in order to highlight animals that may require human inspection.

The software stack consists of a FastAPI backend, Ultralytics YOLO for cattle detection, OpenCV for media processing, SQLite for persistence, and a React dashboard. Behaviour labels such as standing, walking/moving, resting/lying, and low activity are produced by rule-based analysis of bounding-box motion and shape. An experimental risk score in the range 0–100 is mapped to bands: Normal, Monitor, Attention Required, and High Attention.

The project is explicitly **not** a veterinary diagnostic device. Outputs are phrased as possible health concerns or abnormal activity. A demonstration dataset is seeded so the product can be presented without access to a live farm, and is labelled DEMO DATA so it is never confused with real inference.

The completed MVP supports image upload, video upload with background processing, optional webcam analysis, animal history, alerts, and charts suitable for a project viva.
