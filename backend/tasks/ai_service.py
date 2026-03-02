"""
OpenRouter AI Service
Handles communication with OpenRouter API for AI-powered features
"""

import requests
from decouple import config
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# OpenRouter API Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = config('OPENROUTER_API_KEY', default='')
DEFAULT_MODEL = config('OPENROUTER_MODEL', default='openai/gpt-3.5-turbo')


class OpenRouterError(Exception):
    """Custom exception for OpenRouter API errors"""
    pass


class AIService:
    """Service class for interacting with OpenRouter AI API"""
    
    def __init__(self):
        """Initialize AI service with API configuration"""
        self.api_url = OPENROUTER_API_URL
        self.api_key = OPENROUTER_API_KEY
        self.default_model = DEFAULT_MODEL
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not configured in environment")
    
    def _make_request(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a request to OpenRouter API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: AI model to use (defaults to configured model)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters for the API
            
        Returns:
            API response as dictionary
            
        Raises:
            OpenRouterError: If API request fails
        """
        if not self.api_key:
            raise OpenRouterError("OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://taskflow.app",  
            "X-Title": "Taskflow"  
        }
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
       
        payload.update(kwargs)
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error("OpenRouter API request timed out")
            raise OpenRouterError("Request timed out. Please try again.")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"OpenRouter API HTTP error: {e.response.status_code} - {e.response.text}")
            
            if e.response.status_code == 401:
                raise OpenRouterError("Invalid API key")
            elif e.response.status_code == 429:
                raise OpenRouterError("Rate limit exceeded. Please try again later.")
            elif e.response.status_code >= 500:
                raise OpenRouterError("OpenRouter service is temporarily unavailable")
            else:
                raise OpenRouterError(f"API request failed: {e.response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request error: {str(e)}")
            raise OpenRouterError("Failed to connect to AI service")
    
    def generate_task_suggestions(
        self,
        context: str,
        num_suggestions: int = 3
    ) -> list:
        """
        Generate task suggestions based on context
        
        Args:
            context: Context or description to generate tasks from
            num_suggestions: Number of task suggestions to generate
            
        Returns:
            List of suggested tasks
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful task management assistant. "
                    "Generate clear, actionable task suggestions based on the given context. "
                    f"Provide exactly {num_suggestions} task suggestions. "
                    "Format each task as a brief title (max 100 characters)."
                )
            },
            {
                "role": "user",
                "content": f"Generate {num_suggestions} task suggestions for: {context}"
            }
        ]
        
        try:
            response = self._make_request(
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )
            
            
            content = response["choices"][0]["message"]["content"]
            
            
            suggestions = []
            for line in content.strip().split('\n'):
                line = line.strip()
               
                if line and not line.startswith('#'):
                   
                    cleaned = line.lstrip('0123456789.-*• ').strip()
                    if cleaned:
                        suggestions.append(cleaned)
            
            return suggestions[:num_suggestions]
            
        except OpenRouterError:
            raise
        except Exception as e:
            logger.error(f"Error parsing task suggestions: {str(e)}")
            raise OpenRouterError("Failed to parse AI response")
    
    def enhance_task_description(
        self,
        title: str,
        description: str = ""
    ) -> str:
        """
        Enhance a task description with more details and clarity
        
        Args:
            title: Task title
            description: Current task description (optional)
            
        Returns:
            Enhanced description
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful task management assistant. "
                    "Enhance task descriptions to be clear, actionable, and well-structured. "
                    "Keep descriptions concise but comprehensive (2-4 sentences). "
                    "Include key steps or considerations if relevant."
                )
            },
            {
                "role": "user",
                "content": f"Task: {title}\nCurrent description: {description or 'None'}\n\nProvide an enhanced description:"
            }
        ]
        
        try:
            response = self._make_request(
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            
            content = response["choices"][0]["message"]["content"].strip()
            return content
            
        except OpenRouterError:
            raise
        except Exception as e:
            logger.error(f"Error enhancing task description: {str(e)}")
            raise OpenRouterError("Failed to parse AI response")
    
    def analyze_task_priority(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a task and suggest priority level with reasoning
        
        Args:
            title: Task title
            description: Task description
            due_date: Due date if available
            
        Returns:
            Dictionary with 'priority' (high/medium/low) and 'reasoning'
        """
        due_info = f" Due date: {due_date}" if due_date else ""
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful task management assistant. "
                    "Analyze tasks and suggest priority levels (high/medium/low). "
                    "Respond in JSON format: {\"priority\": \"high|medium|low\", \"reasoning\": \"brief explanation\"}"
                )
            },
            {
                "role": "user",
                "content": f"Task: {title}\nDescription: {description or 'None'}{due_info}\n\nAnalyze priority:"
            }
        ]
        
        try:
            response = self._make_request(
                messages=messages,
                temperature=0.5,
                max_tokens=150
            )
            
            content = response["choices"][0]["message"]["content"].strip()
            
            
            import json
            try:
                result = json.loads(content)
                if "priority" in result and "reasoning" in result:
                    return result
            except json.JSONDecodeError:
                pass
            
            
            content_lower = content.lower()
            if "high" in content_lower:
                priority = "high"
            elif "low" in content_lower:
                priority = "low"
            else:
                priority = "medium"
                
            return {
                "priority": priority,
                "reasoning": content
            }
            
        except OpenRouterError:
            raise
        except Exception as e:
            logger.error(f"Error analyzing task priority: {str(e)}")
            raise OpenRouterError("Failed to parse AI response")
    
    def breakdown_task(
        self,
        title: str,
        description: str = "",
        num_steps: int = 5
    ) -> Dict[str, Any]:
        """
        Break down a task into smaller, actionable subtasks
        
        Args:
            title: Task title
            description: Task description
            num_steps: Number of subtasks to generate (1-10)
            
        Returns:
            Dictionary with 'subtasks' list and optional 'notes'
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful task management assistant that breaks down complex tasks into smaller, actionable steps. "
                    f"Generate {num_steps} specific, actionable subtasks. "
                    "Each subtask should be clear, focused, and achievable. "
                    "Respond in JSON format: {\"subtasks\": [\"step 1\", \"step 2\", ...], \"notes\": \"optional helpful notes\"}"
                )
            },
            {
                "role": "user",
                "content": f"Break down this task:\n\nTitle: {title}\nDescription: {description or 'No additional details'}\n\nProvide {num_steps} actionable subtasks:"
            }
        ]
        
        try:
            response = self._make_request(
                messages=messages,
                temperature=0.7,
                max_tokens=400
            )
            
            content = response["choices"][0]["message"]["content"].strip()
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(content)
                if "subtasks" in result and isinstance(result["subtasks"], list):
                    return {
                        "subtasks": result["subtasks"][:num_steps],
                        "notes": result.get("notes", "")
                    }
            except json.JSONDecodeError:
                pass
            
            # Fallback: extract steps from text
            subtasks = []
            for line in content.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove numbering and bullet points
                    cleaned = line.lstrip('0123456789.-*• ').strip()
                    if cleaned and not cleaned.lower().startswith('note'):
                        subtasks.append(cleaned)
            
            return {
                "subtasks": subtasks[:num_steps] if subtasks else ["Review task requirements", "Plan approach", "Execute task", "Review results"],
                "notes": "AI-generated task breakdown"
            }
            
        except OpenRouterError:
            raise
        except Exception as e:
            logger.error(f"Error breaking down task: {str(e)}")
            raise OpenRouterError("Failed to parse AI response")


ai_service = AIService()
