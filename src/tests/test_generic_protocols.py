from opengeodeweb_viewer.generic.generic_protocols import VtkGenericView
class_ = VtkGenericView()

def test_register(server):
    print(class_.prefix + class_.schemas_dict["register"]["rpc"], flush=True)
    server.call(class_.prefix + class_.schemas_dict["register"]["rpc"], [{"viewer_object": "mesh", "id": "123456789", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "mesh/register.jpeg") == True
