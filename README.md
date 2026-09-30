# Сервис расчета энергопотребления систем видеонаблюдения

**Тема 9**: Расчет энергопотребления системы видеонаблюдения.  
- **Услуги**: модели камер (`cameras`) — количество, тип, мощность (`power`, Вт), разрешение (`resolution`), уличная/для помещения (`housing_type`).  
- **Заявка**: расчет общего суточного потребления (кВт·ч) и стоимости эксплуатации системы за месяц.

Стек: Python 3 + FastAPI + SQLAlchemy 2.0 (asyncpg) + Alembic + PostgreSQL + Jinja2.

---

## 1. Структура базы данных (3 таблицы)

Каскадное удаление строго запрещено (`ondelete="RESTRICT"`).

### 1.1. Таблица `cameras` (Услуги по теме)
| Поле | Тип | Nullable | Описание |
|---|---|---|---|
| `id` | Integer (PK) | No | Уникальный идентификатор камеры |
| `model_name` | String(100) | No | Название модели камеры |
| `description` | String(500) | Yes | Краткое описание камеры |
| `status` | String(20) | No | Статус: `draft`, `published`, `deleted` |
| `image_url` | String(255) | Yes | URL / путь к файлу изображения |
| `video_url` | String(255) | Yes | URL / путь к файлу видео |
| `power` | Float | Yes | Потребляемая мощность (Вт) |
| `resolution` | String(50) | Yes | Разрешение матрицы |
| `housing_type` | String(50) | Yes | Тип корпуса (уличная / для помещения) |
| `created_at` | DateTime (TZ) | No | Дата и время создания (default now) |
| `published_at` | DateTime (TZ) | Yes | Дата и время публикации |
| `creator_id` | Integer (FK `users.id`) | No | Владелец/создатель карточки (`RESTRICT`) |

### 1.2. Таблица `users` (Пользователи)
| Поле | Тип | Nullable | Описание |
|---|---|---|---|
| `id` | Integer (PK) | No | Уникальный идентификатор пользователя |
| `username` | String(50) | No | Уникальное имя пользователя |
| `password` | String(100) | No | Пароль пользователя |

### 1.3. Таблица `camera_likes` (Связь M-M Пользователи — Камеры)
| Поле | Тип | Nullable | Описание |
|---|---|---|---|
| `id` | Integer (PK) | No | Первичный ключ записи лайка |
| `user_id` | Integer (FK `users.id`) | No | Идентификатор пользователя (`RESTRICT`) |
| `camera_id` | Integer (FK `cameras.id`) | No | Идентификатор камеры (`RESTRICT`) |
*Уникальное ограничение*: `uq_camera_user_like (user_id, camera_id)`.

---

## 2. Спецификация REST API (Строго 10 методов, префикс `/api`)

Интерактивная документация Swagger UI доступна по адресу: `http://localhost:8000/docs`.

### Домен камер (`/api/cameras`) — 7 методов

| № | Метод | URL | Описание | Входные параметры | Коды ответов |
|---|---|---|---|---|---|
| 1 | `GET` | `/api/cameras` | Список опубликованных камер с фильтрацией | `power_max: Optional[float]` (Query) | `200 OK` (список объектов `CameraResponse` с признаком `is_creator: 0/1`) |
| 2 | `GET` | `/api/cameras/feed` | Лента камер (строго 1 запись с `LIMIT 1`) | `camera_id: Optional[int]`, `next: bool` (Query) | `200 OK` (`CameraResponse`), `404 Not Found` |
| 3 | `GET` | `/api/cameras/draft` | Черновик текущего пользователя (ID=1) | Нет (ID в URL не передается) | `200 OK` (`CameraResponse`), `404 Not Found` |
| 4 | `POST` | `/api/cameras` | Добавление новой камеры (черновик) с загрузкой файлов | `model_name` (Form), `housing_type` (Form), `image_file` (File), `video_file` (File) | `201 Created` (`CameraResponse`), `400 Bad Request` |
| 5 | `PUT` | `/api/cameras/{camera_id}/publish` | Публикация черновика | `camera_id: int` (Path), `CameraPublishRequest` (JSON: power, resolution, etc.) | `200 OK` (`CameraResponse`), `400 Bad Request`, `403 Forbidden`, `404 Not Found` |
| 6 | `DELETE` | `/api/cameras/{camera_id}` | Мягкое логическое удаление (soft delete) | `camera_id: int` (Path) | `200 OK` (`CameraResponse` со статусом `deleted`), `403 Forbidden`, `404 Not Found` |
| 7 | `POST` | `/api/cameras/{camera_id}/like` | Установка / отмена лайка (0/1) | `camera_id: int` (Path), `LikeToggleRequest` (JSON: `{"like": 0/1}`) | `200 OK` (`CameraResponse` с обновленным `likes_count`), `404 Not Found` |

### Домен пользователей (`/api/users`) — 3 метода

| № | Метод | URL | Описание | Входные параметры | Коды ответов |
|---|---|---|---|---|---|
| 8 | `POST` | `/api/users/register` | Регистрация нового пользователя | `UserRegisterRequest` (JSON: `username`, `password`) | `201 Created` (`UserResponse`), `400 Bad Request` |
| 9 | `POST` | `/api/users/login` | Аутентификация пользователя (заглушка для ЛР4) | `UserLoginRequest` (JSON: `username`, `password`) | `200 OK` (`UserLoginResponse`: токен, user_id), `401 Unauthorized` |
| 10 | `POST` | `/api/users/logout` | Завершение сеанса (заглушка для ЛР4) | Нет | `200 OK` |

---

## 3. Запуск и проверка

```bash
# 1. Запуск БД и инфраструктуры
docker compose up -d

# 2. Применение миграций БД
cd app && alembic upgrade head && cd ..

# 3. Запуск веб-сервера
PYTHONPATH=app uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- **Swagger UI**: `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **Веб-интерфейс (ЛР1-2)**: `http://localhost:8000/cameras`
- **Adminer**: `http://localhost:8081`
