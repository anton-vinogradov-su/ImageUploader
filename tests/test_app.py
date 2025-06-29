import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app import app
import io

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "html" in response.text.lower()


def test_list_img():
    response = client.get("/pictures")
    assert response.status_code == 200
    # Можно проверить, что выводится html-страница с изображениями
    assert "html" in response.text.lower()


def test_upload_get():
    response = client.get("/upload")
    assert response.status_code == 200
    assert "html" in response.text.lower()


def test_remove_img_not_found():
    response = client.get("/remove", params={"filename": "nonexistent_file.png"})
    assert response.status_code == 200
    assert "не найден" in response.text.lower()


def test_upload_img_correct():
    # Создаем "фейковый" файл
    file_content = io.BytesIO(b"fake_image_data")
    data = {"file": ("test.png", file_content, "image/png")}

    response = client.post("/upload", files=data)
    assert response.status_code == 200
    json_data = response.json()
    assert "message" in json_data
    assert "успешно" in json_data["message"].lower()


def test_upload_wrong_file_type():
    file_content = io.BytesIO(b"some text data")
    data = {"file": ("test.txt", file_content, "text/plain")}

    response = client.post("/upload", files=data)
    assert response.status_code == 200
    json_data = response.json()
    assert "message" in json_data
    assert "не подходит" in json_data["message"].lower()


def test_upload_without_file():
    response = client.post("/upload", files={})
    assert response.status_code == 422  # FastAPI вернёт 422 если не передан обязательный файл


def test_remove_img_success(tmp_path):
    # Создаем временный файл
    tmp_file = tmp_path / "temp_image.png"
    tmp_file.write_bytes(b"fake image data")

    # Копируем файл в папку images (или другую папку проекта)
    import shutil
    import os
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    shutil.copy(tmp_file, os.path.join(images_dir, tmp_file.name))

    # Пытаемся удалить
    response = client.get("/remove", params={"filename": tmp_file.name})
    assert response.status_code == 200
    assert "успешно" in response.text.lower()
