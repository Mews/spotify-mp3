import ast
from io import BytesIO

from PIL import Image


def load_data_from_file(file_name: str):
    with open("tests/example_responses/" + file_name) as f:
        return ast.literal_eval(f.read())


def mock_image_bytes():
    img = Image.new("RGB", (100, 100), color="red")
    with BytesIO() as output:
        img.save(output, format="JPEG")
        return output.getvalue()
