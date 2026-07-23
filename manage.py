import asyncio
import typer

from app.seeds.task_seeder import run_bulk_seed

app = typer.Typer(
    help="⚡ Корпоративный пульт управления Jira-Backend (PyTask API) ⚡",
    no_args_is_help=True
)

@app.command(name="seed", help="Заполнение базы данных детерминированными тестовыми данными (Bulk Insert)")
def seed_database(
    tasks_per_project: int = typer.Option(
        50, 
        "--tasks", "-t", 
        help="Количество корневых задач, создаваемых для каждого проекта"
    ),
    users_count: int = typer.Option(
        15, 
        "--users", "-u", 
        help="Общее количество генерируемых сотрудников компании"
    )
):
    """Консольная команда для быстрой генерации дерева задач, участников и логов."""
    typer.secho("🚀 Подключение к PostgreSQL и запуск фабрики сидов...", fg=typer.colors.CYAN)
    
    try:
        # Запускаем асинхронную сессию сидера в синхронном окружении Typer
        asyncio.run(run_bulk_seed(users_count=users_count, tasks_count=tasks_per_project))
        
        typer.secho("\n✨ Процесс завершен! Команда успешно выполнена.", fg=typer.colors.GREEN, bold=True)
    except Exception as error:
        typer.secho(f"\n❌ Произошла ошибка при наполнении базы: {error}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
