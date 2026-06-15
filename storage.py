from minio import Minio
from minio.error import S3Error
import boto3
from botocore.exceptions import ClientError
import hashlib
import json
import os
import io
from datetime import datetime
from pathlib import Path

class MinioStorage:
    """
    Универсальное хранилище с поддержкой:
    - S3-совместимые: MinIO, Backblaze B2, Cloudflare R2, AWS S3, DigitalOcean Spaces
    - Локальное файловое хранилище (для бесплатного деплоя)
    """

    def __init__(self):
        """Инициализация хранилища"""
        # Определяем тип хранилища
        self.storage_type = os.getenv('STORAGE_TYPE', 's3').lower()

        if self.storage_type == 'local':
            self._init_local_storage()
        else:
            self._init_s3_storage()

    def _init_local_storage(self):
        """Инициализация локального файлового хранилища"""
        self.storage_type = 'local'
        self.base_path = Path(os.getenv('STORAGE_PATH', './storage/pastes'))
        self.base_path.mkdir(parents=True, exist_ok=True)

        print(f"🗄️ Local Storage Configuration:")
        print(f"   Type: Local Filesystem")
        print(f"   Path: {self.base_path.absolute()}")
        print(f"   ⚠️  Warning: Data will be lost on Render free tier restarts!")
        print(f"   💡 Tip: Use Backblaze B2 (10GB free) for persistent storage")

    def _init_s3_storage(self):
        """Инициализация S3-совместимого хранилища"""
        self.storage_type = 's3'

        # Получаем настройки из переменных окружения
        self.endpoint = os.getenv('S3_ENDPOINT', os.getenv('MINIO_ENDPOINT', 'localhost:9000'))
        self.access_key = os.getenv('S3_ACCESS_KEY', os.getenv('MINIO_ACCESS_KEY', 'minioadmin'))
        self.secret_key = os.getenv('S3_SECRET_KEY', os.getenv('MINIO_SECRET_KEY', 'minioadmin123'))
        self.bucket_name = os.getenv('S3_BUCKET_NAME', os.getenv('MINIO_BUCKET_NAME', 'pastes'))
        self.secure = os.getenv('S3_SECURE', os.getenv('MINIO_SECURE', 'false')).lower() == 'true'
        self.region = os.getenv('S3_REGION', 'us-east-1')

        # Определяем тип провайдера
        self.use_boto3 = False
        if 'backblazeb2.com' in self.endpoint:
            print(f"🗄️ Detected Backblaze B2 - using boto3")
            self.use_boto3 = True
        elif self.endpoint.endswith('amazonaws.com') or self.endpoint == 's3':
            print(f"🗄️ Detected AWS S3")
            self.endpoint = None
        elif 'r2.cloudflarestorage.com' in self.endpoint:
            print(f"🗄️ Detected Cloudflare R2")

        print(f"🗄️ S3 Storage Configuration:")
        print(f"   Endpoint: {self.endpoint or 'AWS S3'}")
        print(f"   Bucket: {self.bucket_name}")
        print(f"   Region: {self.region}")
        print(f"   Secure: {self.secure}")
        print(f"   Using boto3: {self.use_boto3}")

        try:
            if self.use_boto3:
                # Backblaze B2 через boto3 (лучше работает с подписями)
                endpoint_url = f"https://{self.endpoint}" if self.secure else f"http://{self.endpoint}"
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region
                )
                # Не проверяем head_bucket для B2 - некоторые ключи не имеют этого права
                print("✅ Backblaze B2 Storage initialized successfully (boto3)")
                print("   Note: Bucket access will be verified on first write operation")
            else:
                # Minio клиент для других провайдеров
                if self.endpoint:
                    self.client = Minio(
                        self.endpoint,
                        access_key=self.access_key,
                        secret_key=self.secret_key,
                        secure=self.secure,
                        region=self.region
                    )
                else:
                    # AWS S3
                    self.client = Minio(
                        's3.amazonaws.com',
                        access_key=self.access_key,
                        secret_key=self.secret_key,
                        secure=True,
                        region=self.region
                    )
                self._ensure_bucket_exists()
                print("✅ S3 Storage initialized successfully (minio)")

        except Exception as e:
            print(f"❌ S3 Storage initialization error: {e}")
            raise

    def _ensure_bucket_exists(self):
        """Создает bucket если он не существует (только для S3)"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name, location=self.region)
                print(f"✅ Bucket '{self.bucket_name}' created successfully")
            else:
                print(f"✅ Bucket '{self.bucket_name}' already exists")
        except S3Error as e:
            # Для некоторых провайдеров (например, R2) bucket может существовать, но проверка не работает
            print(f"⚠️ Bucket check warning: {e}")
            print(f"   Assuming bucket '{self.bucket_name}' exists")

    # === ЛОКАЛЬНОЕ ХРАНИЛИЩЕ ===

    def _local_save_content(self, paste_id: int, content: str) -> str:
        """Сохраняет содержимое в локальный файл"""
        paste_dir = self.base_path / str(paste_id)
        paste_dir.mkdir(parents=True, exist_ok=True)

        content_file = paste_dir / 'content.txt'
        content_file.write_text(content, encoding='utf-8')

        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return content_hash

    def _local_get_content(self, paste_id: int) -> str:
        """Читает содержимое из локального файла"""
        content_file = self.base_path / str(paste_id) / 'content.txt'
        if not content_file.exists():
            raise FileNotFoundError(f"Paste {paste_id} not found")
        return content_file.read_text(encoding='utf-8')

    def _local_delete_content(self, paste_id: int):
        """Удаляет содержимое из локального хранилища"""
        paste_dir = self.base_path / str(paste_id)
        if paste_dir.exists():
            import shutil
            shutil.rmtree(paste_dir)

    def _local_save_metadata(self, paste_id: int, metadata: dict):
        """Сохраняет метаданные в локальный файл"""
        paste_dir = self.base_path / str(paste_id)
        paste_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = paste_dir / 'metadata.json'
        metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')

    def _local_get_metadata(self, paste_id: int) -> dict:
        """Читает метаданные из локального файла"""
        metadata_file = self.base_path / str(paste_id) / 'metadata.json'
        if not metadata_file.exists():
            return {}
        return json.loads(metadata_file.read_text(encoding='utf-8'))

    # === УНИВЕРСАЛЬНЫЕ МЕТОДЫ ===

    def save_paste_content(self, paste_id: int, content: str) -> str:
        """Сохраняет содержимое пасты и возвращает хеш"""
        if self.storage_type == 'local':
            content_hash = self._local_save_content(paste_id, content)
            print(f"✅ Paste {paste_id} saved to local storage")
            return content_hash

        # S3 хранилище
        try:
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            object_name = f"{paste_id}/content.txt"
            content_bytes = content.encode('utf-8')

            if self.use_boto3:
                # Backblaze B2 через boto3
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=content_bytes,
                    ContentType='text/plain; charset=utf-8'
                )
            else:
                # Minio клиент
                content_stream = io.BytesIO(content_bytes)
                self.client.put_object(
                    self.bucket_name,
                    object_name,
                    content_stream,
                    length=len(content_bytes),
                    content_type='text/plain; charset=utf-8'
                )

            print(f"✅ Paste {paste_id} saved to S3 storage")
            return content_hash

        except (S3Error, ClientError) as e:
            print(f"❌ S3 save error: {e}")
            raise

    def get_paste_content(self, paste_id: int, content_hash: str) -> str:
        """Получает содержимое пасты"""
        if self.storage_type == 'local':
            content = self._local_get_content(paste_id)
            print(f"✅ Paste {paste_id} loaded from local storage (length: {len(content)})")
            return content

        # S3 хранилище
        try:
            object_name = f"{paste_id}/content.txt"

            if self.use_boto3:
                # Backblaze B2 через boto3
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
                content = response['Body'].read().decode('utf-8')
            else:
                # Minio клиент
                response = self.client.get_object(self.bucket_name, object_name)
                content = response.read().decode('utf-8')
                response.close()
                response.release_conn()

            print(f"✅ Paste {paste_id} loaded from S3 storage (length: {len(content)})")
            return content

        except (S3Error, ClientError) as e:
            print(f"❌ S3 read error for paste {paste_id}: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error loading paste {paste_id}: {e}")
            raise

    def delete_paste_content(self, paste_id: int, content_hash: str):
        """Удаляет содержимое пасты"""
        if self.storage_type == 'local':
            self._local_delete_content(paste_id)
            print(f"✅ Paste {paste_id} deleted from local storage")
            return

        # S3 хранилище
        try:
            object_name = f"{paste_id}/content.txt"

            if self.use_boto3:
                # Backblaze B2 через boto3
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            else:
                # Minio клиент
                self.client.remove_object(self.bucket_name, object_name)

            print(f"✅ Paste {paste_id} deleted from S3 storage")

        except (S3Error, ClientError) as e:
            print(f"❌ S3 delete error: {e}")
            raise

    def save_paste_metadata(self, paste_id: int, metadata: dict):
        """Сохраняет метаданные пасты"""
        if self.storage_type == 'local':
            self._local_save_metadata(paste_id, metadata)
            print(f"✅ Paste {paste_id} metadata saved to local storage")
            return

        # S3 хранилище
        try:
            object_name = f"{paste_id}/metadata.json"
            metadata_json = json.dumps(metadata, ensure_ascii=False, indent=2)
            metadata_bytes = metadata_json.encode('utf-8')

            if self.use_boto3:
                # Backblaze B2 через boto3
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=metadata_bytes,
                    ContentType='application/json; charset=utf-8'
                )
            else:
                # Minio клиент
                metadata_stream = io.BytesIO(metadata_bytes)
                self.client.put_object(
                    self.bucket_name,
                    object_name,
                    metadata_stream,
                    length=len(metadata_bytes),
                    content_type='application/json; charset=utf-8'
                )

            print(f"✅ Paste {paste_id} metadata saved to S3 storage")

        except (S3Error, ClientError) as e:
            print(f"❌ Metadata save error: {e}")
            raise

    def get_paste_metadata(self, paste_id: int) -> dict:
        """Получает метаданные пасты"""
        if self.storage_type == 'local':
            return self._local_get_metadata(paste_id)

        # S3 хранилище
        try:
            object_name = f"{paste_id}/metadata.json"

            if self.use_boto3:
                # Backblaze B2 через boto3
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
                metadata_json = response['Body'].read().decode('utf-8')
            else:
                # Minio клиент
                response = self.client.get_object(self.bucket_name, object_name)
                metadata_json = response.read().decode('utf-8')
                response.close()
                response.release_conn()

            metadata = json.loads(metadata_json)
            print(f"✅ Paste {paste_id} metadata loaded from S3 storage")
            return metadata

        except (S3Error, ClientError) as e:
            print(f"⚠️ Metadata read error: {e}")
            return {}

    def list_paste_files(self, paste_id: int) -> list:
        """Список файлов пасты"""
        if self.storage_type == 'local':
            paste_dir = self.base_path / str(paste_id)
            if not paste_dir.exists():
                return []

            files = []
            for file_path in paste_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        'name': str(file_path.relative_to(self.base_path)),
                        'size': stat.st_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime)
                    })
            return files

        # S3 хранилище
        try:
            prefix = f"{paste_id}/"
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)

            files = []
            for obj in objects:
                files.append({
                    'name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified
                })

            return files

        except S3Error as e:
            print(f"❌ List files error: {e}")
            return []

    def rename_paste_content(self, old_id: int, new_id: int, content_hash: str):
        """Переименовывает файл содержимого пасты"""
        if self.storage_type == 'local':
            old_dir = self.base_path / str(old_id)
            new_dir = self.base_path / str(new_id)
            if old_dir.exists():
                old_dir.rename(new_dir)
            print(f"✅ Content renamed from {old_id} to {new_id}")
            return

        # S3 хранилище
        try:
            old_object_name = f"{old_id}/content.txt"
            new_object_name = f"{new_id}/content.txt"

            response = self.client.get_object(self.bucket_name, old_object_name)
            content = response.read()
            response.close()
            response.release_conn()

            content_stream = io.BytesIO(content)
            self.client.put_object(
                self.bucket_name,
                new_object_name,
                content_stream,
                length=len(content),
                content_type='text/plain; charset=utf-8'
            )

            self.client.remove_object(self.bucket_name, old_object_name)
            print(f"✅ Content renamed from {old_id} to {new_id}")

        except S3Error as e:
            print(f"❌ Rename error: {e}")
            raise

    def delete_paste_metadata(self, paste_id: int):
        """Удаляет метаданные пасты"""
        if self.storage_type == 'local':
            metadata_file = self.base_path / str(paste_id) / 'metadata.json'
            if metadata_file.exists():
                metadata_file.unlink()
            print(f"✅ Paste {paste_id} metadata deleted from local storage")
            return

        # S3 хранилище
        try:
            object_name = f"{paste_id}/metadata.json"

            if self.use_boto3:
                # Backblaze B2 через boto3
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            else:
                # Minio клиент
                self.client.remove_object(self.bucket_name, object_name)

            print(f"✅ Paste {paste_id} metadata deleted from S3 storage")

        except (S3Error, ClientError) as e:
            print(f"⚠️ Metadata delete error: {e}")

    def get_bucket_info(self) -> dict:
        """Получает информацию о хранилище"""
        if self.storage_type == 'local':
            return {
                'storage_type': 'local',
                'path': str(self.base_path.absolute()),
                'warning': 'Data will be lost on Render free tier restarts'
            }

        # S3 хранилище
        try:
            return {
                'storage_type': 's3',
                'bucket_name': self.bucket_name,
                'endpoint': self.endpoint or 'AWS S3',
                'region': self.region
            }
        except Exception as e:
            print(f"⚠️ Bucket info error: {e}")
            return {
                'storage_type': 's3',
                'bucket_name': self.bucket_name,
                'endpoint': self.endpoint or 'AWS S3',
                'region': self.region
            }
