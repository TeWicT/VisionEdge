import pytest
from ui.vision_ui import VisionEdgeUI

def test_display_live_feed_positive():
    ui = VisionEdgeUI()
    assert ui.display_live_feed()

def test_show_anomalies_positive():
    ui = VisionEdgeUI()
    result = ui.show_anomalies({"x": 10, "y": 5})
    assert result is True

def test_show_anomalies_negative():
    ui = VisionEdgeUI()
    with pytest.raises(Exception):
        ui.show_anomalies(None)