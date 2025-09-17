from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
import os
from pathlib import Path
from shutil import copyfile
from opengeodeweb_viewer.database.connection import db_manager
from opengeodeweb_microservice.database.data import Data


def _prepare_dataset(
    *,
    id: str,
    geode_object: str,
    viewable_file_name: str,
) -> str:
    tests_root = Path(__file__).resolve().parents[1]
    src_data = tests_root / "data"
    data_root = os.environ.get("DATA_FOLDER_PATH")
    assert data_root, "DATA_FOLDER_PATH non défini"
    dest_dir = Path(data_root) / id
    dest_dir.mkdir(parents=True, exist_ok=True)

    src_file = src_data / viewable_file_name
    dst_file = dest_dir / viewable_file_name
    copyfile(src_file, dst_file)

    session = db_manager.get_session()
    try:
        row = session.get(Data, id)
        if row is None:
            session.add(
                Data(
                    id=id,
                    native_file_name="",
                    viewable_file_name=viewable_file_name,
                    geode_object=geode_object,
                    light_viewable=None,
                    input_file="",
                    additional_files=[],
                )
            )
        else:
            row.viewable_file_name = viewable_file_name
            row.geode_object = geode_object
        session.commit()
    finally:
        session.close()
    return id

def test_register_model(server):

    _prepare_dataset(id="123456789", geode_object="model", viewable_file_name="CrossSection.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/register.jpeg") == True


def test_register_model_cube(server):

    _prepare_dataset(id="123456789", geode_object="model", viewable_file_name="cube.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/cube_register.jpeg") == True


def test_visibility_model(server):

    test_register_model(server)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "model/visibility.jpeg") == True


def test_deregister_model(server):

    test_register_model(server)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/deregister.jpeg") == True
