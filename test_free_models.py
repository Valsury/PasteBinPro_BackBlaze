#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы AI помощника с бесплатными моделями
"""

import os
import sys

# Добавляем путь к проекту
sys.path.append('.')

# Устанавливаем переменные окружения для тестов
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['LLM_API_KEY'] = 'test-key'  # Для тестов используем тестовый ключ
os.environ['APP_URL'] = 'http://localhost:5000'

from llm_helper import UniversalLLMHelper

def test_free_models():
    """Тест бесплатных моделей"""
    print("🤖 Тестирование AI помощника с бесплатными моделями")
    print("=" * 50)
    
    # Создаем экземпляр помощника
    helper = UniversalLLMHelper()
    
    print(f"Провайдер: {helper.provider}")
    print(f"Текущая модель: {helper.model}")
    
    # Получаем список доступных моделей
    print("\n📋 Получение списка моделей...")
    models = helper.get_available_models()
    
    print(f"Всего доступно моделей: {len(models)}")
    print("Список бесплатных моделей:")
    for i, model in enumerate(models[:15], 1):  # Показываем первые 15
        is_free = ':free' in model
        free_marker = ' 🆓' if is_free else ''
        print(f"  {i:2d}. {model}{free_marker}")
    
    if len(models) > 15:
        print(f"    ... и еще {len(models) - 15} моделей")
    
    # Проверяем, что все модели в списке действительно бесплатные
    print("\n🔍 Проверка моделей на бесплатность...")
    
    # Определяем логику проверки, аналогичную улучшенной фильтрации
    def is_model_free(model):
        model_lower = model.lower()
        
        # Гарантированно бесплатные модели
        guaranteed_free_models = [
            'mistralai/mistral-7b-instruct',
            'google/gemini-flash-1.5',
            'google/gemini-flash-latest',
            'meta-llama/llama-3-8b-instruct',
            'meta-llama/llama-3.1-8b-instruct',
            'meta-llama/llama-3.2-3b-instruct',
            'meta-llama/llama-3.2-11b-vision-instruct',
            'meta-llama/llama-3.3-70b-instruct'
        ]
        
        if model in guaranteed_free_models:
            return True
        
        # Модели с тегом :free
        if ':free' in model:
            return True
        
        # Ключевые слова для бесплатных моделей
        free_keywords = [
            ':free',
            'free',
            'mistralai/mistral-',
            'google/gemini-flash',
            'meta-llama/llama-3',
            'meta-llama/llama-3.1',
            'meta-llama/llama-3.2',
            'meta-llama/llama-3.3',
            'nousresearch/nous-hermes',
            'cognitivecomputations/dolphin',
            'qwen/qwen3',
            'poolside/laguna',
            'liquid/lfm',
            'openai/gpt-oss'
        ]
        
        # Платные исключения
        paid_exceptions = [
            'mistralai/mistral-large',
            'mistralai/mistral-medium-',
            'mistralai/mistral-small-',
            'mistralai/mistral-saba',
            'mistralai/mistral-nemo',
            'mistralai/mistral-large-',
            'mistralai/mistral-medium-',
            'mistralai/mistral-small-'
        ]
        
        # Для моделей Google Gemma и Nvidia Nemotron принимаем только с :free
        if 'google/gemma' in model or 'nvidia/nemotron' in model:
            return ':free' in model
        
        # Проверяем ключевые слова и исключения
        has_free_keyword = any(keyword in model_lower for keyword in free_keywords)
        is_paid_exception = any(exception in model for exception in paid_exceptions)
        
        return has_free_keyword and not is_paid_exception
    
    free_models = []
    non_free_models = []
    
    for model in models:
        if is_model_free(model):
            free_models.append(model)
        else:
            non_free_models.append(model)
    
    print(f"✅ Бесплатных моделей: {len(free_models)}")
    print(f"⚠️  Платных моделей: {len(non_free_models)}")
    
    if non_free_models:
        print("\n🚫 Платные модели, обнаруженные в списке:")
        for model in non_free_models:
            print(f"  - {model}")
        print("\n⚠️  НЕДОПУСТИМО! В списке есть платные модели!")
    else:
        print("\n🎉 ОТЛИЧНО! Все модели в списке бесплатные!")
    
    # Тестируем переключение модели
    print("\n🔄 Тестирование переключения моделей...")
    if models:
        test_model = models[0] if len(models) > 0 else 'mistralai/mistral-7b-instruct'
        print(f"Пробуем установить модель: {test_model}")
        success = helper.set_model(test_model)
        print(f"Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
        print(f"Текущая модель после установки: {helper.model}")
    
    # Тестируем установку несуществующей модели
    print("\n🚫 Тестирование установки несуществующей модели...")
    non_existent_model = 'openai/gpt-4-turbo'  # Платная модель
    success = helper.set_model(non_existent_model)
    print(f"Пробуем установить: {non_existent_model}")
    print(f"Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    print(f"Текущая модель после попытки: {helper.model}")
    
    # Проверяем доступность API
    print("\n📡 Проверка доступности API...")
    is_available = helper.is_available()
    print(f"API доступен: {'✅ Да' if is_available else '❌ Нет'}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")
    
    # Сводка
    print("\n📊 Сводка:")
    print(f"  • Всего моделей в списке: {len(models)}")
    print(f"  • Бесплатных моделей: {len(free_models)}")
    print(f"  • Платных моделей: {len(non_free_models)}")
    print(f"  • API доступен: {'Да' if is_available else 'Нет'}")
    
    if non_free_models:
        print("\n⚠️  КРИТИЧЕСКАЯ ОШИБКА: В списке есть платные модели!")
        print("   Немедленно исправьте фильтрацию в llm_helper.py")
        return False
    else:
        print("\n🎉 СИСТЕМА РАБОТАЕТ КОРРЕКТНО! Все модели бесплатные!")
        return True

def test_model_filter():
    """Тест фильтрации моделей по бесплатности"""
    print("\n🔧 Тест фильтрации моделей")
    print("=" * 50)
    
    # Тестовый список моделей (имитация ответа от API)
    test_models = [
        'mistralai/mistral-7b-instruct',           # Бесплатная
        'google/gemini-flash-1.5',                 # Бесплатная
        'meta-llama/llama-3-8b-instruct',          # Бесплатная
        'nousresearch/nous-hermes-2-mixtral-8x7b-dpo',  # Бесплатная
        'openai/gpt-4-turbo',                      # Платная
        'anthropic/claude-3-opus-20240229',        # Платная
        'google/gemma-4-26b-a4b-it:free',          # Бесплатная (с :free)
        'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free',  # Бесплатная
        'openai/gpt-3.5-turbo',                    # Платная
    ]
    
    # Ключевые слова для бесплатных моделей
    free_keywords = ['mistral', 'gemini', 'llama', 'nous', ':free']
    
    print("Тестовый список моделей:")
    for model in test_models:
        is_free = any(keyword in model.lower() for keyword in free_keywords)
        status = '🆓' if is_free else '💲'
        print(f"  {status} {model}")
    
    # Фильтрация
    free_models = [m for m in test_models if any(kw in m.lower() for kw in free_keywords)]
    paid_models = [m for m in test_models if not any(kw in m.lower() for kw in free_keywords)]
    
    print(f"\n📊 Результаты фильтрации:")
    print(f"  Бесплатных моделей: {len(free_models)}")
    print(f"  Платных моделей: {len(paid_models)}")
    
    if paid_models:
        print("\n🚫 Платные модели, которые будут отфильтрованы:")
        for model in paid_models:
            print(f"  - {model}")

if __name__ == "__main__":
    print("🧪 Тестирование системы бесплатных моделей AI помощника")
    print("=" * 60)
    
    test_free_models()
    test_model_filter()
    
    print("\n" + "=" * 60)
    print("🎉 Все тесты завершены!")