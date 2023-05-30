from enum import StrEnum
from typing import Protocol
import io
from uuid import uuid4

from fastapi import UploadFile
from settings.config import settings

from minio import Minio
from shared.utils import urljoin


class StorageTypeEnum(StrEnum):
    courses: str = "courses"
    tests: str = "tests"
    player: str = "player"


class IStorage(Protocol):
    def _save(self, file: UploadFile, path_prefix: str | None = None):
        ...

    def save_course_file(self, file: UploadFile, path_prefix: str | None = None):
        ...

    def save_test_file(self, file: UploadFile, path_prefix: str | None = None):
        ...

    def save_player_file(self, file: UploadFile, path_prefix: str | None = None):
        ...


class LocalStorage(IStorage):
    def __init__(self):
        self._bucket_name = settings.s3_settings.bucket_name
        self.minio = self.__set_connection()

    def __set_connection(self):
        minio_client = Minio(
            endpoint=settings.s3_settings.endpoint_url,
            access_key=settings.s3_settings.access_key_id,
            secret_key=settings.s3_settings.secret_access_key,
            secure=False,
        )
        return minio_client

    def _get_path(
        self, filename: str, folder: str, path_prefix: str | None = None
    ) -> str:
        if path_prefix:
            return urljoin(folder, path_prefix, filename)
        return urljoin(folder, filename)

    def _save(
        self, file: UploadFile, folder: StorageTypeEnum, path_prefix: str | None = None
    ):
        _file = io.BytesIO(file.file.read())

        file_path = self._get_path(f"{str(uuid4())}.zip", folder.value, path_prefix)
        print(file_path)
        self.minio.put_object(
            self._bucket_name,
            file_path,
            data=_file,
            content_type=file.content_type,
            length=file.size,
        )

        return file_path

    def save_course_file(self, file: UploadFile, path_prefix: str | None = None) -> str:
        return self._save(file, StorageTypeEnum.courses, path_prefix)

    def save_test_file(self, file: UploadFile, path_prefix: str | None = None):
        ...

    def save_player_file(self, file: UploadFile, path_prefix: str | None = None):
        ...
