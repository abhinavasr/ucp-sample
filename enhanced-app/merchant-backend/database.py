"""Database configuration and models using SQLAlchemy."""

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

Base = declarative_base()


class Product(Base):
    """Product model for persistent storage."""
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    category = Column(String)
    brand = Column(String)
    image_url = Column(Text)  # JSON array of image URLs
    availability = Column(String, default="https://schema.org/InStock")
    condition = Column(String, default="https://schema.org/NewCondition")
    gtin = Column(String)
    mpn = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def to_schema_org(self):
        """Convert to Schema.org Product format compatible with business_agent."""
        return {
            "@type": "Product",
            "productID": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "image": json.loads(self.image_url) if self.image_url else [],
            "brand": {"@type": "Brand", "name": self.brand} if self.brand else None,
            "offers": {
                "@type": "Offer",
                "price": str(self.price),
                "priceCurrency": self.currency,
                "availability": self.availability,
                "itemCondition": self.condition
            },
            "category": self.category,
            "gtin": self.gtin,
            "mpn": self.mpn
        }


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, database_url: str = "sqlite+aiosqlite:///./enhanced_app.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None

    def init_db(self):
        """Initialize database connection and create tables."""
        # For SQLite, use synchronous engine for table creation
        sync_url = self.database_url.replace("+aiosqlite", "")
        sync_engine = create_engine(sync_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=sync_engine)

        # Create async session maker
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            future=True
        )
        self.SessionLocal = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_session(self):
        """Get database session."""
        async with self.SessionLocal() as session:
            yield session


# Global database manager instance
# Get database URL from environment variable or use default
database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./enhanced_app.db")
db_manager = DatabaseManager(database_url)
