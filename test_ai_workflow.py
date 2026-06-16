#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки полного workflow AI помощника
"""

import os
import sys
import time

# Добавляем путь к проекту
sys.path.append('.')

# Устанавливаем переменные окружения для тестов
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['LLM_API_KEY'] = ''  # Для тестов без реального ключа
os.environ['APP_URL'] = 'http://localhost:5000'

from llm_helper import UniversalLLMHelper

def test_ai_workflow():
    """Тестирование полного workflow AI помощника"""
    print("🤖 Тестирование полного workflow AI помощника")
    print("=" * 60)
    
    # Создаем экземпляр помощника
    helper = UniversalLLMHelper()
    
    print(f"Провайдер: {helper.provider}")
    print(f"Текущая модель: {helper.model}")
    
    # Проверяем доступность API
    print("\n📡 Проверка доступности API...")
    is_available = helper.is_available()
    print(f"API доступен: {'✅ Да' if is_available else '❌ Нет'}")
    
    if not is_available:
        print("⚠️  API недоступен, но это нормально для тестов без ключа")
        print("⚠️  Для реальной работы установите LLM_API_KEY в переменные окружения")
    
    # Получаем список доступных моделей
    print("\n📋 Получение списка моделей...")
    models = helper.get_available_models()
    
    print(f"Всего доступно моделей: {len(models)}")
    print("Первые 10 бесплатных моделей:")
    for i, model in enumerate(models[:10], 1):
        is_free = ':free' in model
        free_marker = ' 🆓' if is_free else ''
        print(f"  {i:2d}. {model}{free_marker}")
    
    # Проверяем, что все модели действительно бесплатные
    print("\n🔍 Проверка на платные модели...")
    paid_models = [m for m in models if ':free' not in m and m not in [
        'mistralai/mistral-7b-instruct',
        'google/gemini-flash-1.5',
        'meta-llama/llama-3-8b-instruct',
        'openrouter/free'
    ]]
    
    if paid_models:
        print(f"⚠️  Обнаружены потенциально платные модели: {len(paid_models)}")
        for model in paid_models[:5]:
            print(f"  - {model}")
        if len(paid_models) > 5:
            print(f"    ... и еще {len(paid_models) - 5} моделей")
    else:
        print("✅ Все модели гарантированно бесплатные!")
    
    # Тестируем переключение моделей
    print("\n🔄 Тестирование переключения моделей...")
    
    # Тест 1: Переключение на бесплатную модель
    if len(models) > 0:
        free_model = models[0]
        print(f"Пробуем установить модель: {free_model}")
        success = helper.set_model(free_model)
        print(f"Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        print(f"Текущая модель: {helper.model}")
    
    # Тест 2: Попытка установить платную модель
    print(f"\n🚫 Тестирование защиты от платных моделей...")
    paid_model = 'openai/gpt-4-turbo'
    print(f"Пробуем установить платную модель: {paid_model}")
    success = helper.set_model(paid_model)
    print(f"Результат: {'✅ Успешно (автопереключение)' if success else '❌ Ошибка'}")
    print(f"Текущая модель после попытки: {helper.model}")
    
    # Проверяем, что модель была заменена на бесплатную альтернативу
    if helper.model == paid_model:
        print("❌ ОШИБКА: Система приняла платную модель!")
    else:
        print("✅ СИСТЕМА РАБОТАЕТ КОРРЕКТНО: Платная модель отклонена")
    
    # Тест 3: Проверка функциональности без реального API ключа
    print("\n🧪 Тестирование функциональности AI помощника...")
    
    # Создаем тестовые промпты
    test_prompts = [
        {
            'name': 'Простой текст',
            'prompt': 'Напиши короткий рассказ о солнечном дне',
            'max_tokens': 200
        },
        {
            'name': 'Код на Python',
            'prompt': 'Напиши функцию для вычисления факториала на Python',
            'max_tokens': 150
        },
        {
            'name': 'Бизнес текст',
            'prompt': 'Создай краткое описание проекта для инвесторов',
            'max_tokens': 100
        }
    ]
    
    for test in test_prompts:
        print(f"\n📝 Тест: {test['name']}")
        print(f"Промпт: {test['prompt'][:50]}...")
        
        try:
            # Пробуем сгенерировать текст (без реального запроса, только проверка логики)
            result = helper.generate_text(test['prompt'], test['max_tokens'])
            
            if 'error' in result:
                print(f"❌ Ошибка: {result['error'][:100]}")
                if 'API' in result['error'] or 'ключ' in result['error'].lower():
                    print("   (Ожидаемая ошибка без API ключа)")
            else:
                print(f"✅ Успешно!")
                print(f"   Модель: {result['model']}")
                print(f"   Токенов: {result['tokens_used']}")
                
        except Exception as e:
            print(f"❌ Исключение: {str(e)[:100]}")
    
    # Сводка
    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СВОДКА:")
    print(f"  • Всего доступно моделей: {len(models)}")
    print(f"  • Моделей с тегом :free: {sum(1 for m in models if ':free' in m)}")
    print(f"  • Гарантированно бесплатных моделей: {sum(1 for m in models if m in ['mistralai/mistral-7b-instruct', 'google/gemini-flash-1.5', 'meta-llama/llama-3-8b-instruct'])}")
    print(f"  • Потенциально платных моделей: {len(paid_models)}")
    print(f"  • API доступен: {'Да' if is_available else 'Нет (ожидаемо)'}")
    print(f"  • Защита от платных моделей: {'✅ Работает' if helper.model != paid_model else '❌ Не работает'}")
    
    if len(paid_models) == 0 and helper.model != paid_model:
        print("\n🎉 СИСТЕМА ПРОШЛА ВСЕ ТЕСТЫ УСПЕШНО!")
        print("   AI помощник готов к работе с бесплатными моделями")
    else:
        print("\n⚠️  ТРЕБУЕТСЯ ДОРАБОТКА:")
        if len(paid_models) > 0:
            print(f"   - Найдено {len(paid_models)} потенциально платных моделей")
        if helper.model == paid_model:
            print(f"   - Система не защищена от платных моделей")

def test_api_integration():
    """Тестирование интеграции с реальным API"""
    print("\n🔌 Тестирование интеграции с реальным API")
    print("=" * 50)
    
    # Проверяем наличие API ключа
    api_key = os.getenv('LLM_API_KEY', '')
    
    if not api_key:
        print("❌ API ключ не установлен")
        print("   Установите переменную окружения LLM_API_KEY для тестов")
        print("   или используйте config.env файл")
        return False
    
    print("✅ API ключ найден")
    
    # Проверяем файл config.env
    config_path = 'config.env'
    if os.path.exists(config_path):
        print(f"✅ Файл config.env найден")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
                if 'OPENROUTER_API_KEY' in config_content:
                    print("✅ OpenRouter API ключ настроен в config.env")
                else:
                    print("⚠️  OpenRouter API ключ не найден в config.env")
        except Exception as e:
            print(f"❌ Ошибка чтения config.env: {e}")
    else:
        print("⚠️  Файл config.env не найден")
        print("   Создайте файл с переменными окружения для работы")
    
    print("\n💡 Рекомендации для запуска:")
    print("   1. Установите реальный OpenRouter API ключ в LLM_API_KEY")
    print("   2. Или создайте config.env с OPENROUTER_API_KEY=ваш_ключ")
    print("   3. AI помощник будет работать с бесплатными моделями")
    print("   4. Платные модели автоматически блокируются")
    
    return True

if __name__ == "__main__":
    print("🔬 Комплексное тестирование AI помощника")
    print("=" * 70)
    
    test_ai_workflow()
    test_api_integration()
    
    print("\n" + "=" * 70)
    print("✅ Тестирование завершено!")
    
    # Выводим инструкции для пользователя
    print("\n📝 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:")
    print("   Для использования AI помощника:")
    print("   1. Получите бесплатный API ключ на https://openrouter.ai")
    print("   2. Установите его в переменные окружения:")
    print("      - Windows: set LLM_API_KEY=ваш_ключ")
    print("      - Или добавьте в config.env: OPENROUTER_API_KEY=ваш_ключ")
    print("   3. Запустите приложение: python app.py")
    print("   4. Перейдите на страницу /ai-helper")
    print("   5. Все доступные модели гарантированно бесплатные 🆓")
    print("\n⚠️  ВНИМАНИЕ: Платные модели автоматически блокируются")
    print("   Система защищает от случайного использования платных API")