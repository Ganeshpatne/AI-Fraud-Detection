"""
Database seeder – populates sample users and transactions for demo purposes.
Run: python -m backend.seed_data
"""
import asyncio
import random
import json
import uuid
from datetime import datetime, timedelta

from backend.database import async_session, init_db
from backend.models.database_models import User, Transaction, FraudLog, RiskScore, Alert
from backend.services.fraud_engine import fraud_engine
from backend.utils.auth import hash_password


SAMPLE_USERS = [
    {"username": "admin", "email": "admin@fraudshield.ai", "location": "Mumbai, IN", "device_fingerprint": "dev-admin-001", "role": "admin", "password": "admin123"},
    {"username": "analyst", "email": "analyst@fraudshield.ai", "location": "Pune, IN", "device_fingerprint": "dev-analyst-002", "role": "analyst", "password": "analyst123"},
    {"username": "ganesh_patne", "email": "ganesh@example.com", "location": "Mumbai, IN", "device_fingerprint": "dev-ganesh-001", "role": "admin", "password": "ganesh123"},
    {"username": "sujal_surve", "email": "sujal@example.com", "location": "Pune, IN", "device_fingerprint": "dev-sujal-002", "role": "analyst", "password": "sujal123"},
    {"username": "aditya_tambadkar", "email": "aditya@example.com", "location": "Delhi, IN", "device_fingerprint": "dev-aditya-003", "role": "analyst", "password": "aditya123"},
    {"username": "priya_sharma", "email": "priya@example.com", "location": "Bangalore, IN", "device_fingerprint": "dev-priya-004", "role": "user", "password": "priya123"},
    {"username": "rahul_verma", "email": "rahul@example.com", "location": "Chennai, IN", "device_fingerprint": "dev-rahul-005", "role": "user", "password": "rahul123"},
    {"username": "john_doe", "email": "john@example.com", "location": "New York, US", "device_fingerprint": "dev-john-006", "role": "user", "password": "john1234"},
]

LOCATIONS = [
    "Mumbai, IN", "Pune, IN", "Delhi, IN", "Bangalore, IN", "Chennai, IN",
    "New York, US", "London, UK", "Tokyo, JP", "Lagos, NG", "Moscow, RU",
    "São Paulo, BR", "Sydney, AU", "Dubai, AE",
]

MERCHANTS = [
    "Amazon", "Flipkart", "Walmart", "Target", "Best Buy",
    "Netflix", "Uber", "Swiggy", "Zomato", "Gas Station",
    "Luxury Jewelers", "Electronics Hub", "Crypto Exchange",
]

CATEGORIES = ["shopping", "food", "travel", "entertainment", "utilities", "crypto", "transfer"]


async def seed():
    await init_db()

    async with async_session() as db:
        # Check if data exists
        from sqlalchemy import select, func
        count = (await db.execute(select(func.count(User.id)))).scalar()
        if count > 0:
            print(f"Database already has {count} users. Skipping seed.")
            return

        # Create users
        users = []
        for u_data in SAMPLE_USERS:
            password = u_data.pop("password")
            role = u_data.pop("role", "user")
            user = User(
                id=str(uuid.uuid4()),
                password_hash=hash_password(password),
                role=role,
                **u_data,
            )
            db.add(user)
            users.append(user)
        await db.flush()
        print(f"Created {len(users)} users (with auth credentials).")
        print("  Default logins: admin/admin123, analyst/analyst123, ganesh_patne/ganesh123")

        # Removed dummy transaction seeding for a clean production demonstration state
        # The database is completely blank aside from authorized users.
        await db.commit()
        print("Database is clean and ready for real dataset uploads.")


if __name__ == "__main__":
    asyncio.run(seed())
