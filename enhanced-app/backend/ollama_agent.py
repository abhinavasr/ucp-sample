"""Ollama-powered chat agent extending business_agent functionality."""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Any, Optional
import json
from sqlalchemy import select
from database import Product, db_manager


class EnhancedBusinessAgent:
    """Enhanced business agent using Ollama LLM."""

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
        self.tools = self._create_tools()
        self.agent = None
        self._initialize_agent()

    def _create_tools(self) -> List:
        """Create tools for the agent."""

        @tool
        async def search_shopping_catalog(query: str) -> str:
            """
            Search the product catalog for items matching the query.
            Returns a JSON list of matching products with details.

            Args:
                query: Search terms (e.g., "cookies", "chips", "snacks")
            """
            async for session in db_manager.get_session():
                # Search by name, category, or description
                stmt = select(Product).where(
                    Product.is_active == True
                ).where(
                    (Product.name.ilike(f"%{query}%")) |
                    (Product.category.ilike(f"%{query}%")) |
                    (Product.description.ilike(f"%{query}%"))
                )
                result = await session.execute(stmt)
                products = result.scalars().all()

                if not products:
                    return json.dumps({"message": "No products found matching your query.", "products": []})

                product_list = [p.to_schema_org() for p in products]
                return json.dumps({
                    "message": f"Found {len(products)} product(s)",
                    "products": product_list
                })

        @tool
        def add_to_checkout(
            checkout_id: str,
            product_id: str,
            quantity: int = 1,
            session_id: str = "default"
        ) -> str:
            """
            Add a product to the checkout cart.

            Args:
                checkout_id: Unique checkout session ID
                product_id: Product ID to add
                quantity: Quantity to add (default: 1)
                session_id: User session identifier
            """
            if checkout_id not in self.checkouts:
                self.checkouts[checkout_id] = {
                    "id": checkout_id,
                    "session_id": session_id,
                    "line_items": [],
                    "currency": "USD",
                    "status": "incomplete",
                    "customer": {},
                    "totals": {}
                }

            checkout = self.checkouts[checkout_id]

            # Check if product already in cart
            for item in checkout["line_items"]:
                if item["product_id"] == product_id:
                    item["quantity"] += quantity
                    self._recalculate_checkout(checkout_id)
                    return json.dumps({
                        "message": f"Updated quantity for product {product_id}",
                        "checkout": checkout
                    })

            # Add new line item
            checkout["line_items"].append({
                "product_id": product_id,
                "quantity": quantity
            })

            self._recalculate_checkout(checkout_id)
            return json.dumps({
                "message": f"Added product {product_id} to checkout",
                "checkout": checkout
            })

        @tool
        def remove_from_checkout(checkout_id: str, product_id: str) -> str:
            """
            Remove a product from the checkout cart.

            Args:
                checkout_id: Unique checkout session ID
                product_id: Product ID to remove
            """
            if checkout_id not in self.checkouts:
                return json.dumps({"error": "Checkout not found"})

            checkout = self.checkouts[checkout_id]
            checkout["line_items"] = [
                item for item in checkout["line_items"]
                if item["product_id"] != product_id
            ]

            self._recalculate_checkout(checkout_id)
            return json.dumps({
                "message": f"Removed product {product_id} from checkout",
                "checkout": checkout
            })

        @tool
        def update_checkout(checkout_id: str, product_id: str, quantity: int) -> str:
            """
            Update the quantity of a product in checkout.

            Args:
                checkout_id: Unique checkout session ID
                product_id: Product ID to update
                quantity: New quantity (0 to remove)
            """
            if quantity == 0:
                return remove_from_checkout(checkout_id, product_id)

            if checkout_id not in self.checkouts:
                return json.dumps({"error": "Checkout not found"})

            checkout = self.checkouts[checkout_id]
            for item in checkout["line_items"]:
                if item["product_id"] == product_id:
                    item["quantity"] = quantity
                    self._recalculate_checkout(checkout_id)
                    return json.dumps({
                        "message": f"Updated quantity to {quantity}",
                        "checkout": checkout
                    })

            return json.dumps({"error": "Product not found in checkout"})

        @tool
        def get_checkout(checkout_id: str) -> str:
            """
            Get current checkout details.

            Args:
                checkout_id: Unique checkout session ID
            """
            if checkout_id not in self.checkouts:
                return json.dumps({"error": "Checkout not found"})

            return json.dumps({"checkout": self.checkouts[checkout_id]})

        @tool
        def update_customer_details(
            checkout_id: str,
            email: str,
            shipping_address: Optional[Dict[str, str]] = None
        ) -> str:
            """
            Update customer email and shipping information.

            Args:
                checkout_id: Unique checkout session ID
                email: Customer email address
                shipping_address: Shipping address dict with street, city, state, zip, country
            """
            if checkout_id not in self.checkouts:
                return json.dumps({"error": "Checkout not found"})

            checkout = self.checkouts[checkout_id]
            checkout["customer"]["email"] = email

            if shipping_address:
                checkout["customer"]["shipping_address"] = shipping_address

            return json.dumps({
                "message": "Customer details updated",
                "checkout": checkout
            })

        @tool
        def start_payment(checkout_id: str) -> str:
            """
            Initialize payment process for checkout.

            Args:
                checkout_id: Unique checkout session ID
            """
            if checkout_id not in self.checkouts:
                return json.dumps({"error": "Checkout not found"})

            checkout = self.checkouts[checkout_id]

            if not checkout["line_items"]:
                return json.dumps({"error": "Checkout is empty"})

            if "email" not in checkout.get("customer", {}):
                return json.dumps({"error": "Customer email required"})

            checkout["status"] = "ready_for_payment"
            return json.dumps({
                "message": "Ready for payment",
                "checkout": checkout,
                "payment_required": True
            })

        @tool
        def complete_checkout(checkout_id: str, payment_token: str = "mock_token") -> str:
            """
            Complete the checkout and create an order.

            Args:
                checkout_id: Unique checkout session ID
                payment_token: Payment authorization token
            """
            if checkout_id not in self.checkouts:
                return json.dumps({"error": "Checkout not found"})

            checkout = self.checkouts[checkout_id]

            if checkout["status"] != "ready_for_payment":
                return json.dumps({"error": "Checkout not ready for completion"})

            # Create order
            import time
            order_id = f"ORD-{int(time.time())}"
            order = {
                "id": order_id,
                "checkout_id": checkout_id,
                "items": checkout["line_items"],
                "customer": checkout["customer"],
                "totals": checkout["totals"],
                "payment_token": payment_token,
                "status": "completed",
                "created_at": time.time()
            }

            self.orders[order_id] = order
            checkout["status"] = "completed"

            return json.dumps({
                "message": "Order placed successfully!",
                "order": order
            })

        return [
            search_shopping_catalog,
            add_to_checkout,
            remove_from_checkout,
            update_checkout,
            get_checkout,
            update_customer_details,
            start_payment,
            complete_checkout
        ]

    def _recalculate_checkout(self, checkout_id: str):
        """Recalculate checkout totals including tax and shipping."""
        checkout = self.checkouts[checkout_id]

        # This would normally fetch product details from DB
        # For now, we'll use placeholder logic
        subtotal = 0.0
        for item in checkout["line_items"]:
            # In real implementation, fetch price from DB
            item_price = 5.00  # Placeholder
            item["line_total"] = item_price * item["quantity"]
            subtotal += item["line_total"]

        tax = subtotal * 0.10  # 10% tax
        shipping = 5.00 if subtotal > 0 else 0.00
        total = subtotal + tax + shipping

        checkout["totals"] = {
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "shipping": round(shipping, 2),
            "total": round(total, 2),
            "currency": "USD"
        }

    def _initialize_agent(self):
        """Initialize the LangChain agent."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful shopping assistant for an online store.

You can help customers:
- Search for products in our catalog
- Add items to their shopping cart
- Manage their checkout (add, remove, update quantities)
- Collect shipping information
- Process payments and complete orders

Be friendly, helpful, and guide customers through the shopping process.
Always confirm actions and provide clear feedback.

When showing products, describe them clearly and mention the price.
When customers want to buy something, add it to their checkout and show the current cart status.
"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

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
            result = await self.agent_executor.ainvoke({
                "input": message,
                "chat_history": chat_history or []
            })

            return {
                "output": result["output"],
                "session_id": session_id,
                "status": "success"
            }
        except Exception as e:
            return {
                "output": f"I apologize, but I encountered an error: {str(e)}",
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }
