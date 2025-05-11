import pytest
from models.yolo_model import YOLOModel

def test_detect_objects_positive():
    model = YOLOModel()
    result = model.detect_objects("test_image_with_objects.jpg")
    assert len(result) >= 1

def test_train_model_positive():
    model = YOLOModel()
    metrics = model.train_model("sample_dataset_path")
    assert "accuracy" in metrics

def test_detect_objects_negative():
    model = YOLOModel()
    with pytest.raises(ValueError):
        model.detect_objects(None)

def test_train_model_negative():
    model = YOLOModel()
    with pytest.raises(Exception):
        model.train_model("/empty/folder")