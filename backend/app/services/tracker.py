"""Simple IoU + centroid tracker for video cattle IDs.

This is a college-project tracker, not a production MOT system.
IDs can switch under occlusion, camera motion, or crowded scenes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.detector import Detection


def iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter <= 0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def centroid_distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


@dataclass
class Track:
    track_id: int
    label: str
    bbox: tuple[float, float, float, float]
    centroid: tuple[float, float]
    confidence: float
    hits: int = 1
    disappeared: int = 0
    first_frame: int = 0
    last_frame: int = 0
    history: list[dict] = field(default_factory=list)
    total_distance: float = 0.0
    time_visible: float = 0.0

    def as_detection_like(self) -> Detection:
        x1, y1, x2, y2 = self.bbox
        return Detection(
            class_name="cow",
            confidence=self.confidence,
            x=x1,
            y=y1,
            width=x2 - x1,
            height=y2 - y1,
        )


class CattleTracker:
    def __init__(self, max_disappeared: int = 20, iou_threshold: float = 0.25, max_distance: float = 180.0):
        self.max_disappeared = max_disappeared
        self.iou_threshold = iou_threshold
        self.max_distance = max_distance
        self.next_id = 1
        self.tracks: dict[int, Track] = {}

    def _new_label(self) -> str:
        label = f"Cow #{self.next_id:02d}"
        self.next_id += 1
        return label

    def update(self, detections: list[Detection], frame_index: int, timestamp: float) -> list[Track]:
        if not self.tracks:
            for det in detections:
                self._register(det, frame_index, timestamp)
            return list(self.tracks.values())

        if not detections:
            to_delete = []
            for track_id, track in self.tracks.items():
                track.disappeared += 1
                if track.disappeared > self.max_disappeared:
                    to_delete.append(track_id)
            for track_id in to_delete:
                del self.tracks[track_id]
            return list(self.tracks.values())

        track_ids = list(self.tracks.keys())
        unmatched_tracks = set(track_ids)
        unmatched_dets = set(range(len(detections)))
        pairs: list[tuple[float, int, int]] = []

        for t_idx, track_id in enumerate(track_ids):
            track = self.tracks[track_id]
            for d_idx, det in enumerate(detections):
                overlap = iou(track.bbox, det.xyxy)
                dist = centroid_distance(track.centroid, det.centroid)
                score = overlap if overlap >= self.iou_threshold else (0.15 if dist < self.max_distance else 0.0)
                if score > 0:
                    # Prefer IoU, then closer centroids.
                    pairs.append((-(overlap) + dist / 1000.0, t_idx, d_idx))

        pairs.sort()
        used_tracks = set()
        used_dets = set()
        for _cost, t_idx, d_idx in pairs:
            if t_idx in used_tracks or d_idx in used_dets:
                continue
            used_tracks.add(t_idx)
            used_dets.add(d_idx)
            track_id = track_ids[t_idx]
            self._update_track(self.tracks[track_id], detections[d_idx], frame_index, timestamp)
            unmatched_tracks.discard(track_id)
            unmatched_dets.discard(d_idx)

        for track_id in list(unmatched_tracks):
            track = self.tracks[track_id]
            track.disappeared += 1
            if track.disappeared > self.max_disappeared:
                del self.tracks[track_id]

        for d_idx in unmatched_dets:
            self._register(detections[d_idx], frame_index, timestamp)

        return [t for t in self.tracks.values() if t.disappeared == 0]

    def _register(self, det: Detection, frame_index: int, timestamp: float) -> Track:
        label = self._new_label()
        track_id = self.next_id - 1
        track = Track(
            track_id=track_id,
            label=label,
            bbox=det.xyxy,
            centroid=det.centroid,
            confidence=det.confidence,
            first_frame=frame_index,
            last_frame=frame_index,
        )
        track.history.append(
            {
                "frame": frame_index,
                "t": timestamp,
                "centroid": det.centroid,
                "bbox": det.xyxy,
                "confidence": det.confidence,
            }
        )
        self.tracks[track_id] = track
        return track

    def _update_track(self, track: Track, det: Detection, frame_index: int, timestamp: float) -> None:
        dist = centroid_distance(track.centroid, det.centroid)
        track.total_distance += dist
        track.bbox = det.xyxy
        track.centroid = det.centroid
        track.confidence = det.confidence
        track.hits += 1
        track.disappeared = 0
        track.last_frame = frame_index
        if timestamp > 0 and len(track.history) > 0:
            track.time_visible = max(track.time_visible, timestamp - track.history[0]["t"])
        track.history.append(
            {
                "frame": frame_index,
                "t": timestamp,
                "centroid": det.centroid,
                "bbox": det.xyxy,
                "confidence": det.confidence,
            }
        )
        if len(track.history) > 240:
            track.history = track.history[-240:]
