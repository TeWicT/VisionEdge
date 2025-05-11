import pytest
from core.video_processor import VideoProcessor

def test_process_live_stream_positive():
    vp = VideoProcessor()
    result = vp.process_live_stream("test_cam_01")
    assert result == "Stream started"

def test_process_video_file_positive():
    vp = VideoProcessor()
    result = vp.process_video_file("test_anomaly_video.mp4")
    assert "anomaly" in result.lower()

def test_process_live_stream_negative():
    vp = VideoProcessor()
    with pytest.raises(Exception):
        vp.process_live_stream("nonexistent_cam")

def test_process_video_file_negative():
    vp = VideoProcessor()
    with pytest.raises(FileNotFoundError):
        vp.process_video_file("invalid_path.mp4")