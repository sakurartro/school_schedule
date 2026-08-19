import os
from urllib.parse import urlparse

import aiohttp

YANDEX_HOSTS = (
    "disk.yandex.ru",
    "disk.yandex.com",
    "disk.yandex.by",
    "disk.yandex.kz",
    "disk.yandex.uz",
    "yadi.sk",
)
MAX_FILE_SIZE = 20 * 1024 * 1024
TIMEOUT = aiohttp.ClientTimeout(total=60)


def is_yandex_link(link: str) -> bool:
    """Ссылка ведёт на публичный файл Яндекс.Диска, а не на произвольный хост."""
    host = (urlparse(link).hostname or "").lower().removeprefix("www.")
    return host in YANDEX_HOSTS


class YandexDiskParsing:
    def __init__(self, public_key: str, file_path: str = "tables/table.xlsx"):
        self.public_key = public_key
        self.file_path = file_path
        self.base_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
        self.meta_url = "https://cloud-api.yandex.net/v1/disk/public/resources"
        self.last_hash: str | None = None

    async def download_data(self) -> bool:
        if not is_yandex_link(self.public_key):
            return False

        payload = {"public_key": self.public_key}
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                async with session.get(self.base_url, params=payload) as response:
                    if response.status != 200:
                        return False
                    data = await response.json()

                file_link = data.get("href")
                if not file_link:
                    return False

                async with session.get(file_link) as file:
                    if file.status != 200:
                        return False
                    return await self._write_file(file)
        except (aiohttp.ClientError, TimeoutError):
            return False

    async def _write_file(self, response: aiohttp.ClientResponse) -> bool:
        """Пишем во временный файл, чтобы неудачная загрузка не портила прошлую таблицу."""
        os.makedirs(os.path.dirname(self.file_path) or ".", exist_ok=True)
        tmp_path = f"{self.file_path}.part"
        size = 0
        with open(tmp_path, "wb") as f:
            async for chunk in response.content.iter_chunked(64 * 1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    f.close()
                    os.remove(tmp_path)
                    return False
                f.write(chunk)
        os.replace(tmp_path, self.file_path)
        return True

    async def update_data(self) -> bool:
        if not is_yandex_link(self.public_key):
            return False

        payload = {"public_key": self.public_key}
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                async with session.get(self.meta_url, params=payload) as response:
                    if response.status != 200:
                        return False
                    meta = await response.json()
        except (aiohttp.ClientError, TimeoutError):
            return False

        current_hash = meta.get("md5")
        if current_hash == self.last_hash:
            return False
        self.last_hash = current_hash
        return await self.download_data()
