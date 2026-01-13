"""Simplified Ollama-powered chat agent for shopping assistance."""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Any, Optional
import json
from sqlalchemy import select
from database import Product, db_manager


class EnhancedBusinessAgent:
    """Enhanced business agent using Ollama LLM - simplified version."""

    def __init__(
        self,
        ollama_url: str = "http://host.docker.internal:11434",
        model_name: str = "qwen2.5:latest"
    ):
        self.llm = ChatOllama(
            base_url=ollama_url,
            model=model_name,
            temperature=0.7,
        )
        self.checkouts = {}  # In-memory checkout sessions
        self.orders = {}  # In-memory order history
        self.system_prompt = """You are a helpful shopping assistant for an online store.

You can help customers:
- Search for products in our catalog
- Answer questions about products
- Help them find what they need

Be friendly, helpful, and guide customers through the shopping experience.
Always provide clear, concise responses.

When customers ask about products, I will provide you with the product information from our database.
"""

    async def search_products(self, query: str = None, limit: int = 10) -> List[Dict]:
        """Search for products in the database."""
        async for session in db_manager.get_session():
            stmt = select(Product).where(Product.is_active == True)

            if query:
                search_term = f"%{query.lower()}%"
                stmt = stmt.where(
                    (Product.name.ilike(search_term)) |
                    (Product.description.ilike(search_term)) |
                    (Product.category.ilike(search_term))
                )

            stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            products = result.scalars().all()

            return [{
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "category": p.category,
                "brand": p.brand
            } for p in products]

    async def process_message(
        self,
        message: str,
        session_id: str = "default",
        chat_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return agent response.

        Args:
            message: User input message
            session_id: Session identifier
            chat_history: Previous conversation history

        Returns:
            Response dict with output and metadata
        """
        try:
            # Check if user is asking about products
            search_keywords = ['product', 'cookie', 'chip', 'strawberr', 'show', 'what', 'find', 'looking for']
            should_search = any(keyword in message.lower() for keyword in search_keywords)

            product_context = ""
            if should_search:
                # Extract potential search query
                products = await self.search_products()
                if products:
                    product_context = "\n\nAvailable products:\n"
                    for p in products:
                        product_context += f"- {p['name']} (${p['price']}) - {p['description']}\n"

            # Build conversation messages
            messages = [SystemMessage(content=self.system_prompt)]

            if chat_history:
                messages.extend(chat_history)

            user_message = message
            if product_context:
                user_message += product_context

            messages.append(HumanMessage(content=user_message))

            # Get response from LLM
            response = await self.llm.ainvoke(messages)

            return {
                "output": response.content,
                "session_id": session_id,
                "status": "success"
            }

        except Exception as e:
            return {
                "output": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "session_id": session_id,
                "status": "error"
            }
