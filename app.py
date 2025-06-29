from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path
import logging
from datetime import datetime
from utils.file_utils import is_allowed_file, MAX_FILE_SIZE, get_unique_name

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / "app.log"

logging.basicConfig(
    level=logging.ERROR,
    format="[{asctime}] - {levelname}: {message}",
    style="{",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logging.debug('отдаём index.html')
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/pictures", response_class=HTMLResponse)
async def list_img(request: Request):
    logging.debug(f'Отображаем список изображений')
    image_dir = Path("./images")
    image_files = [f for ext in ("*.png", "*.jpg", "*.jpeg", "*.gif") for f in image_dir.glob(ext)]
    image_list = []

    for f in image_files:
        image_list.append({
            "name": f.name,
            "created": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d") #  %H:%M:%S
        })

    return templates.TemplateResponse(request, "images.html", {"request": request, "images": image_list})


@app.get("/upload", response_class=HTMLResponse)
async def upload_img(request: Request):
    logging.debug(f'отдаём upload.html')
    return templates.TemplateResponse(request, "upload.html", {"request": request})


@app.get("/remove", response_class=HTMLResponse)
async def remove_img(request: Request, filename: str):
    logging.debug(f'Удаляем файл: {filename}')
    image_dir = Path("./images")
    file_path = image_dir / filename
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
        return PlainTextResponse(f"Файл {filename} успешно удалён.")
    else:
        return PlainTextResponse(f"Файл {filename} не найден.")


@app.post("/upload")
async def upload_img(request: Request, file: UploadFile = File(...)):
    logging.debug(f'Файл получен {file.filename}')
    my_file = Path(file.filename)
    if is_allowed_file(my_file):
        logging.debug('Верное расширение')
    else:
        logging.error('Выбрали файл с не верным расширением')
        logging.debug('НЕ верное расширение')
        return {'message': f'Расширение файла {file.filename} не подходит.'}

    content = await file.read(MAX_FILE_SIZE + 1)
    size = len(content)
    if size < MAX_FILE_SIZE:
        logging.debug(f"Длина изображения подходит {size}")
    else:
        logging.debug(f"Длина изображения НЕ подходит {size}")
        return {'message': f'Размер файла {file.filename} не подходит.'}

    new_file_name = get_unique_name(my_file)
    logging.debug(f"Сохраняем новый файл: {new_file_name}")

    image_dir = Path("images")
    image_dir.mkdir(exist_ok=True)
    save_path = image_dir / new_file_name

    save_path.write_bytes(content)
    logging.debug(f"Файл {str(save_path)} записан.")

    return {'message': f'Файл {file.filename} успешно получен!\nСохраним в {save_path}'}


if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
