# mqtt-vm-emulator

Эмулятор виртуальных машин, которые шлют статус/логи и принимают команды через RabbitMQ (AMQP). Управление — через FastAPI.

## Требования

- Python ≥ 3.12
- [uv](https://github.com/astral-sh/uv)
- RabbitMQ на `amqp://guest:guest@localhost/`

## Запуск

```bash
uv sync
uv run python run.py
```

Сервис поднимется на `http://0.0.0.0:8000`. Документация API: `/docs`.

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health` | Healthcheck |
| `POST` | `/api/manager/start_vms?vm_count=N` | Запустить N VM |
| `POST` | `/api/manager/add_vms?vm_count=N` | Добавить ещё N VM |
| `POST` | `/api/manager/stop_vms` | Остановить все VM |
| `POST` | `/api/manager/stop_vm?vm_id=...` | Остановить одну VM |
| `POST` | `/api/manager/ping_vm?vm_id=...` | Пинг VM |
| `GET` | `/api/status/vms_list` | Список активных VM |

## RabbitMQ

- Exchange: `app.events` (topic)
- Команды: `virtual_machines.{vm_id}.commands.*`
- Очередь VM: `virtual_machine.{vm_id}.commands`
