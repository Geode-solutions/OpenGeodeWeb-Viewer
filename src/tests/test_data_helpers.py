import uuid
from typing import Dict, Any, Optional, Tuple


class TestDataRegistry:
    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}

    def create_test_data(self, viewable_file_name: str, geode_object: str) -> str:
        data_id = str(uuid.uuid4())
        self.data[data_id] = {
            "id": data_id,
            "viewable_file_name": viewable_file_name,
            "geode_object": geode_object,
        }
        return data_id

    def get_data(self, data_id: str) -> Optional[Dict[str, Any]]:
        return self.data.get(data_id)

    def find_by_filename(self, filename: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        for data_id, data in self.data.items():
            if data["viewable_file_name"] == filename:
                return data_id, data
        return None

    def remove_data(self, data_id: str) -> bool:
        if data_id in self.data:
            del self.data[data_id]
            return True
        return False

    def clear(self):
        self.data.clear()


test_data_registry = TestDataRegistry()


def create_mesh_data(filename: str) -> str:
    return test_data_registry.create_test_data(filename, "mesh")


def create_model_data(filename: str) -> str:
    return test_data_registry.create_test_data(filename, "model")


def get_or_create_mesh_data(filename: str) -> str:
    existing = test_data_registry.find_by_filename(filename)
    if existing:
        return existing[0]
    return create_mesh_data(filename)


def get_or_create_model_data(filename: str) -> str:
    existing = test_data_registry.find_by_filename(filename)
    if existing:
        return existing[0]
    return create_model_data(filename)
