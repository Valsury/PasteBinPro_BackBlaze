import requests
import json
import os
from typing import Optional, Dict, Any

class UniversalLLMHelper:
    """
    Универсальный помощник для работы с различными LLM API
    Поддерживает: OpenRouter, OpenAI, Anthropic и другие OpenAI-совместимые API
    """

    def __init__(self):
        # Определяем провайдера из переменных окружения
        self.provider = os.getenv('LLM_PROVIDER', 'openrouter').lower()
        self.api_key = os.getenv('LLM_API_KEY', '')
        self.model = os.getenv('LLM_MODEL', 'mistralai/mistral-7b-instruct')

        # Настройки для разных провайдеров
        self.provider_configs = {
            'openrouter': {
                'base_url': 'https://openrouter.ai/api/v1',
                'chat_endpoint': '/chat/completions',
                'models_endpoint': '/models',
                'headers': {
                    'Authorization': f'Bearer {self.api_key}',
                    'HTTP-Referer': os.getenv('APP_URL', 'http://localhost:5000'),
                    'X-Title': 'PasteBin Pro'
                }
            },
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'chat_endpoint': '/chat/completions',
                'models_endpoint': '/models',
                'headers': {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'anthropic': {
                'base_url': 'https://api.anthropic.com/v1',
                'chat_endpoint': '/messages',
                'models_endpoint': None,
                'headers': {
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                }
            },
            'custom': {
                'base_url': os.getenv('LLM_BASE_URL', 'http://localhost:11434/v1'),
                'chat_endpoint': '/chat/completions',
                'models_endpoint': '/models',
                'headers': {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            }
        }

        self.config = self.provider_configs.get(self.provider, self.provider_configs['custom'])
        self.available_models = []

        print(f"🤖 LLM Provider: {self.provider}")
        print(f"🎯 Model: {self.model}")
        print(f"🔗 Base URL: {self.config['base_url']}")

    def is_available(self) -> bool:
        """Проверяет доступность LLM API"""
        try:
            if not self.api_key and self.provider != 'custom':
                print("⚠️ API ключ не установлен")
                return False

            # Для Anthropic проверяем через messages endpoint
            if self.provider == 'anthropic':
                return True  # Пропускаем проверку, проверим при первом запросе

            # Для остальных провайдеров проверяем через models endpoint
            if self.config['models_endpoint']:
                url = f"{self.config['base_url']}{self.config['models_endpoint']}"
                response = requests.get(url, headers=self.config['headers'], timeout=5)
                return response.status_code == 200

            return True
        except Exception as e:
            print(f"❌ Ошибка проверки доступности API: {e}")
            return False

    def get_available_models(self) -> list:
        """Возвращает список доступных моделей"""
        if self.available_models:
            return self.available_models

        try:
            if not self.config['models_endpoint']:
                return [self.model]

            url = f"{self.config['base_url']}{self.config['models_endpoint']}"
            response = requests.get(url, headers=self.config['headers'], timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    self.available_models = [model['id'] for model in data['data']]
                else:
                    self.available_models = [self.model]
            else:
                self.available_models = [self.model]

        except Exception as e:
            print(f"❌ Ошибка получения списка моделей: {e}")
            self.available_models = [self.model]

        return self.available_models

    def set_model(self, model_name: str) -> bool:
        """Устанавливает активную модель"""
        self.model = model_name
        print(f"✅ Модель изменена на: {self.model}")
        return True

    def _make_chat_request(self, messages: list, max_tokens: int = 800, temperature: float = 0.7) -> Dict[str, Any]:
        """Выполняет запрос к Chat API"""
        try:
            url = f"{self.config['base_url']}{self.config['chat_endpoint']}"

            # Формируем payload в зависимости от провайдера
            if self.provider == 'anthropic':
                payload = {
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': max_tokens,
                    'temperature': temperature
                }
            else:
                payload = {
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': max_tokens,
                    'temperature': temperature
                }

            response = requests.post(
                url,
                headers=self.config['headers'],
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()

                # Извлекаем текст ответа в зависимости от провайдера
                if self.provider == 'anthropic':
                    text = result.get('content', [{}])[0].get('text', '')
                else:
                    text = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                return {
                    'success': True,
                    'text': text,
                    'model': self.model,
                    'provider': self.provider
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                return {'error': error_msg}

        except Exception as e:
            error_msg = f"Ошибка запроса: {str(e)}"
            print(f"❌ {error_msg}")
            return {'error': error_msg}

    def generate_text(self, prompt: str, max_tokens: int = 800) -> Dict[str, Any]:
        """Генерирует текст на основе промпта"""
        messages = [
            {'role': 'user', 'content': prompt}
        ]
        return self._make_chat_request(messages, max_tokens)

    # === МЕТОДЫ ГЕНЕРАЦИИ КОДА ===

    def generate_code(self, language: str, description: str, max_tokens: int = 600) -> Dict[str, Any]:
        """Генерирует код на указанном языке"""
        prompt = f"Напиши код на языке {language} для следующей задачи: {description}. Код должен быть рабочим и хорошо прокомментированным."
        return self.generate_text(prompt, max_tokens)

    def improve_code(self, code: str, language: str, description: str, max_tokens: int = 800) -> Dict[str, Any]:
        """Улучшает существующий код"""
        prompt = f"Улучши следующий код на языке {language}:\n\n{code}\n\nОписание улучшений: {description}\n\nПокажи улучшенную версию с объяснениями."
        return self.generate_text(prompt, max_tokens)

    def explain_code(self, code: str, language: str, max_tokens: int = 600) -> Dict[str, Any]:
        """Объясняет код на указанном языке"""
        prompt = f"Объясни следующий код на языке {language} простыми словами:\n\n{code}\n\nОбъяснение должно быть понятным для начинающих программистов."
        return self.generate_text(prompt, max_tokens)

    def generate_documentation(self, code: str, language: str, max_tokens: int = 500) -> Dict[str, Any]:
        """Генерирует документацию для кода"""
        prompt = f"Создай документацию для следующего кода на языке {language}:\n\n{code}\n\nДокументация должна включать описание функций, параметров и примеры использования."
        return self.generate_text(prompt, max_tokens)

    # === УНИВЕРСАЛЬНЫЕ МЕТОДЫ ГЕНЕРАЦИИ ТЕКСТА ===

    def generate_creative_text(self, topic: str, style: str = "общий", max_tokens: int = 800) -> Dict[str, Any]:
        """Генерирует креативный текст на заданную тему"""
        prompt = f"Создай креативный текст в стиле '{style}' на тему '{topic}'. Текст должен быть интересным, оригинальным и захватывающим внимание читателя."
        return self.generate_text(prompt, max_tokens)

    def generate_business_text(self, topic: str, text_type: str = "описание", max_tokens: int = 600) -> Dict[str, Any]:
        """Генерирует бизнес-текст"""
        prompt = f"Создай профессиональный бизнес-текст типа '{text_type}' на тему '{topic}'. Текст должен быть структурированным, убедительным и подходящим для деловой аудитории."
        return self.generate_text(prompt, max_tokens)

    def generate_educational_text(self, topic: str, level: str = "средний", max_tokens: int = 700) -> Dict[str, Any]:
        """Генерирует образовательный текст"""
        prompt = f"Создай образовательный текст уровня '{level}' на тему '{topic}'. Текст должен быть понятным, структурированным и содержать полезную информацию для обучения."
        return self.generate_text(prompt, max_tokens)

    def generate_story(self, genre: str, theme: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Генерирует рассказ или историю"""
        prompt = f"Создай {genre} рассказ на тему '{theme}'. История должна быть увлекательной, с интересными персонажами и захватывающим сюжетом."
        return self.generate_text(prompt, max_tokens)

    def generate_article(self, topic: str, style: str = "информационный", max_tokens: int = 800) -> Dict[str, Any]:
        """Генерирует статью"""
        prompt = f"Напиши {style} статью на тему '{topic}'. Статья должна быть информативной, хорошо структурированной и интересной для чтения."
        return self.generate_text(prompt, max_tokens)

    def generate_social_media_content(self, platform: str, topic: str, tone: str = "дружелюбный", max_tokens: int = 300) -> Dict[str, Any]:
        """Генерирует контент для социальных сетей"""
        prompt = f"Создай {tone} пост для {platform} на тему '{topic}'. Контент должен быть привлекательным, вовлекающим и подходящим для выбранной платформы."
        return self.generate_text(prompt, max_tokens)

    def generate_poem(self, theme: str, style: str = "современный", max_tokens: int = 400) -> Dict[str, Any]:
        """Генерирует стихотворение"""
        prompt = f"Создай {style} стихотворение на тему '{theme}'. Стихотворение должно быть эмоциональным, образным и ритмичным."
        return self.generate_text(prompt, max_tokens)

    def generate_marketing_copy(self, product: str, target_audience: str, max_tokens: int = 500) -> Dict[str, Any]:
        """Генерирует маркетинговый текст"""
        prompt = f"Создай привлекательный маркетинговый текст для продукта '{product}', ориентированный на аудиторию '{target_audience}'. Текст должен быть убедительным и мотивирующим к действию."
        return self.generate_text(prompt, max_tokens)

    def generate_email_template(self, purpose: str, tone: str = "профессиональный", max_tokens: int = 400) -> Dict[str, Any]:
        """Генерирует шаблон email"""
        prompt = f"Создай {tone} шаблон email для {purpose}. Email должен быть четким, вежливым и эффективным в достижении цели."
        return self.generate_text(prompt, max_tokens)

    def generate_presentation_outline(self, topic: str, audience: str, max_tokens: int = 600) -> Dict[str, Any]:
        """Генерирует план презентации"""
        prompt = f"Создай структурированный план презентации на тему '{topic}' для аудитории '{audience}'. План должен включать введение, основные пункты и заключение."
        return self.generate_text(prompt, max_tokens)


# Для обратной совместимости создаем алиас
OllamaHelper = UniversalLLMHelper
