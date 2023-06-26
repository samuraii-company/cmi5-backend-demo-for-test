import io
from shutil import rmtree

from fastapi import UploadFile
from shared.utils import extract_zip
from storage.utils import get_content_type
import os


def test_get_content_type():
    file1, file2 = "index.html", "data.mp4"
    content_type = get_content_type(file1)
    assert content_type == "text/html"
    content_type = get_content_type(file2)
    assert content_type == "application/octet-stream"


def test_extract_zip():
    # need real creating folder for test, need some waining:<
    ARCHIVE_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "./resources/scorm.zip",
    )

    with open(str(ARCHIVE_PATH), "rb") as f:
        scorm_archive = io.BytesIO(f.read())
        file = UploadFile(file=scorm_archive, filename="string")
        path = extract_zip(file)
        assert path
        # delete local folder after test
        rmtree(path)
