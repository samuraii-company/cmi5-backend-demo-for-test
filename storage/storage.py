from enum import StrEnum
import os
from typing import Protocol

from fastapi import UploadFile
from config import settings

from minio import Minio
from shared.utils import urljoin
from storage.utils import get_content_type


class StorageTypeEnum(StrEnum):
    courses: str = "courses"
    tests: str = "tests"
    player: str = "player"


class IStorage(Protocol):
    def _save(self, file: UploadFile, path_prefix: str | None = None):
        ...

    def save_course_folder(self, file_path: str, path_prefix: str | None = None):
        ...


class LocalStorage:
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
        self, _filepath: str, folder: StorageTypeEnum, path_prefix: str | None = None
    ):
        folder_path_on_bucket = (
            os.path.join(folder.value, _filepath, path_prefix)
            if path_prefix
            else os.path.join(folder.value, _filepath)
        )

        for root, _, files in os.walk(_filepath):
            for file in files:
                file_path = os.path.join(root, file)
                object_name = os.path.join(
                    folder_path_on_bucket,
                    os.path.relpath(file_path, _filepath),
                )
                content_type = get_content_type(object_name)
                file_size = os.stat(file_path).st_size

                with open(file_path, "rb") as file_data:
                    self.minio.put_object(
                        self._bucket_name,
                        object_name,
                        file_data,
                        length=file_size,
                        content_type=content_type,
                    )

        return folder_path_on_bucket

    def save_course_folder(self, file_path: str, path_prefix: str | None = None) -> str:
        return self._save(file_path, StorageTypeEnum.courses, path_prefix)
