from dotenv import load_dotenv
import os
import aiohttp
import asyncio


load_dotenv()

DOCUMENT_URL: str = os.getenv("TABLE_LINK", "")

class YandexDiskParsing:
    def __init__(self, public_key: str, file_path: str = "tables/table.xlsx"):
        self.public_key = public_key
        self.file_path = file_path
        self.base_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
        self.meta_url = "https://cloud-api.yandex.net/v1/disk/public/resources"
        self.last_hash: str | None = None


    async def download_data(self) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "public_key": self.public_key
            }
            response = await session.get(self.base_url, params=payload)

            if response.status == 200:
                data = await response.json()

                file_link = data.get("href")

                async with session.get(file_link) as file:
                    content = await file.read()
                    with open(self.file_path, "wb") as f:
                        f.write(content)
                        return "Данные успешно записаны в файл"
            return "Ошибка API"

    async def update_data(self) -> bool:
        async with aiohttp.ClientSession() as session:
            payload = {
                "public_key": self.public_key
            }
            async with session.get(self.meta_url, params=payload) as response:
                if response.status == 200:
                    meta = await response.json()
                    current_hash = meta.get("md5")
                    if current_hash == self.last_hash:
                        return False
                    self.last_hash = current_hash
                    await self.download_data()
                    return True
        return False




async def main():
    yandex_disk = YandexDiskParsing(public_key=DOCUMENT_URL)

    response = await yandex_disk.update_data()

    print(response)


if __name__ == "__main__":
    asyncio.run(main())
        

        