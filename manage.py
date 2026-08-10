import typer
import asyncio

from app.seeds.task_seeder import run_bulk_seed

app = typer.Typer(
    help="⚡ Корпоративный пульт управления Jira-Backend (PyTask API) ⚡",
    no_args_is_help=True
)

@app.command(name="seed", help="Наполнение БД. Создает аккаунты owner@pytask.com, manager@pytask.com, developer@pytask.com")
def seed_database(
    tasks_per_project: int = typer.Option(
        30, 
        "--tasks", "-t", 
        help="Количество корневых ИТ-задач на один проект"
    ),
    users_count: int = typer.Option(
        10, 
        "--users", "-u", 
        help="Общее количество сотрудников (минимум 3 для фиксированных ролей)"
    )
):
    """Консольная команда для быстрой генерации дерева задач, участников и логов."""
    typer.secho("🚀 Подключение к PostgreSQL и запуск фабрики сидов...", fg=typer.colors.CYAN)
    
    try:
        asyncio.run(run_bulk_seed(users_count=users_count, tasks_count=tasks_per_project))
        typer.secho("\n✨ Процесс завершен! Доступы для Swagger: пароль '123' для всех статичных ролей.", fg=typer.colors.GREEN, bold=True)
    except Exception as error:
        typer.secho(f"\n❌ Произошла ошибка при наполнении базы: {error}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)
    
@app.callback()
def main():
    pass

if __name__ == "__main__":
    app()
