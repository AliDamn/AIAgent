from dotenv import load_dotenv
load_dotenv()

from tasks import create_crew

def main():
    print("=" * 80)
    print("AI Business Analyst - Помощник по бизнес-аналитике для банковского сектора")
    print("=" * 80)
    print("\nЭтот AI-агент поможет вам:")
    print("  • Собрать и формализовать бизнес-требования")
    print("  • Создать BRD (Business Requirements Document)")
    print("  • Сгенерировать Use Cases и User Stories")
    print("  • Создать диаграммы процессов (BPMN)")
    print("  • Валидировать качество требований")
    print("  • Подготовить документацию для Confluence")
    print("\n" + "-" * 80)
    
    print("\n Пожалуйста, опишите вашу бизнес-задачу или проблему:")
    print("   (Например: 'Автоматизация обработки заявок на кредит' или 'Улучшение процесса KYC')")
    user_input = input("\n> ").strip()
    
    if not user_input:
        print("\n Ошибка: Вы не ввели описание бизнес-задачи.")
        return
    
    topic = user_input[:50] if len(user_input) > 50 else user_input
    
    print(f"\n Бизнес-задача принята: {topic}")
    print("\n Запуск AI-агентов для анализа и создания документации...")
    print("   Это может занять несколько минут.\n")
    print("=" * 80)
    
    try:
        crew = create_crew(topic, user_input)
        result = crew.kickoff()
        
        print("\n" + "=" * 80)
        print(" Анализ завершен!")
        print("=" * 80)
        print("\n Результаты сохранены в файл: report.txt")
        print("\nСодержимое отчета:")
        print("-" * 80)
        print(result)
        print("-" * 80)
        
    except Exception as e:
        print(f"\n Произошла ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()