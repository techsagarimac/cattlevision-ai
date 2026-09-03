# AI Methodology

## Detection

Object detection is performed with Ultralytics YOLO. The MVP uses a nano COCO checkpoint because it is small, documented, and includes a `cow` class. Confidence default is 0.35. Non-cattle classes are removed in software so people, vehicles, or dogs do not become “cows”.

A custom-trained cattle detector can be dropped in as `models/cattle.pt`. Class names should overlap `CATTLE_CLASS_NAMES` in `detector.py`.

## Tracking

Video IDs are maintained with greedy IoU matching and a centroid-distance fallback. Unmatched tracks increment a disappeared counter and are dropped after a limit. This is comparable in spirit to a simplified SORT and is appropriate for a short student demo clip. It will fail in heavy occlusion; the UI states this.

## Behaviour

Motion speed is the sum of centroid displacements over a short window, divided by bounding-box diagonal so scale is comparable. High aspect ratio (wide, short box) is treated as a lying/recumbent cue. Low speed for an extended visible time is labelled low activity.

Human YOLO-pose checkpoints are **not** used as cattle pose estimators, because transferring human keypoints to livestock would be scientifically misleading. Box-based posture is the honest MVP approach.

## Risk scoring

A transparent additive score combines inactivity, recumbency duration in the clip, extreme aspect ratio, a coefficient-of-variation limp heuristic, and sudden drops in displacement. Thresholds map to four bands. The score is stored and displayed with the disclaimer that it is experimental and non-diagnostic.

## Future ML anomaly model

Observation rows (`movement_score`, `behavior`, box statistics, time of day) form a tabular dataset. A later one-class SVM, autoencoder, or sequence model can consume the same features and write the same `risk_score` field consumed by the dashboard.
