"""
AI utilities for interpreting natural language trading rules.
Supports OpenAI and xAI (X.AI) APIs.
"""
from typing import Optional, Dict, Any
import json
from openai import OpenAI
from config import settings


class AIInterpreter:
    """AI-powered interpreter for natural language trading rules."""
    
    def __init__(self):
        """Initialize AI client based on configured provider."""
        self.provider = settings.default_ai_provider
        
        if self.provider == "openai" and settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = "gpt-4"
        elif self.provider == "xai" and settings.xai_api_key:
            self.client = OpenAI(
                api_key=settings.xai_api_key,
                base_url=settings.xai_api_base
            )
            self.model = "grok-beta"
        else:
            self.client = None
            self.model = None
    
    async def interpret_rule(self, natural_language_rule: str) -> Dict[str, Any]:
        """
        Interpret a natural language trading rule into structured format.
        
        Args:
            natural_language_rule: Human-readable trading rule
            
        Returns:
            Structured rule dictionary with conditions and actions
        """
        if not self.client:
            # Fallback: return a basic structure if no AI is configured
            return {
                "raw_rule": natural_language_rule,
                "conditions": [],
                "actions": [],
                "error": "No AI provider configured"
            }
        
        prompt = f"""
You are a trading rule interpreter. Convert the following natural language trading rule 
into a structured JSON format that can be executed by a trading bot.

Natural Language Rule:
{natural_language_rule}

Output a JSON object with the following structure:
{{
    "symbol": "trading pair symbol (e.g., BTC/USD)",
    "conditions": [
        {{
            "type": "price|volume|indicator|time",
            "operator": "gt|lt|eq|gte|lte",
            "value": "numeric value or expression",
            "description": "human readable condition"
        }}
    ],
    "actions": [
        {{
            "type": "buy|sell|hold",
            "amount": "numeric amount or percentage",
            "order_type": "market|limit",
            "price": "optional price for limit orders",
            "description": "human readable action"
        }}
    ],
    "risk_management": {{
        "stop_loss": "optional stop loss percentage",
        "take_profit": "optional take profit percentage",
        "max_position_size": "optional max position in USD"
    }}
}}

Only return valid JSON, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a trading rule interpreter that outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            # Parse JSON from response
            interpreted_rule = json.loads(content)
            interpreted_rule["raw_rule"] = natural_language_rule
            return interpreted_rule
            
        except Exception as e:
            return {
                "raw_rule": natural_language_rule,
                "conditions": [],
                "actions": [],
                "error": f"Failed to interpret rule: {str(e)}"
            }
    
    async def generate_mutation(self, original_rule: str, mutation_type: str = "random") -> str:
        """
        Generate a mutated version of a trading rule for evolutionary algorithms.
        
        Args:
            original_rule: Original natural language rule
            mutation_type: Type of mutation (random, conservative, aggressive)
            
        Returns:
            Mutated rule text
        """
        if not self.client:
            return original_rule
        
        prompt = f"""
You are helping evolve trading strategies through mutation.

Original Trading Rule:
{original_rule}

Generate a slightly modified version of this rule with a {mutation_type} mutation.
The mutation should:
- Keep the core strategy similar
- Make small adjustments to thresholds, timing, or conditions
- Maintain valid trading logic
- Be a single sentence or paragraph

Return only the new rule text, no explanations.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a trading strategy evolution assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return original_rule
    
    async def crossover_rules(self, rule1: str, rule2: str) -> str:
        """
        Combine two trading rules to create a hybrid strategy.
        
        Args:
            rule1: First parent rule
            rule2: Second parent rule
            
        Returns:
            Hybrid rule combining aspects of both parents
        """
        if not self.client:
            return rule1
        
        prompt = f"""
You are helping evolve trading strategies through crossover (combining strategies).

Parent Rule 1:
{rule1}

Parent Rule 2:
{rule2}

Create a new trading rule that combines elements from both parent rules.
The new rule should:
- Take the best aspects of both strategies
- Create a coherent, logical strategy
- Be a single sentence or paragraph

Return only the new rule text, no explanations.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a trading strategy evolution assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return rule1


# Global AI interpreter instance
ai_interpreter = AIInterpreter()
