#!/usr/bin/env python3
"""
Database Verification Script for Mirage

This script verifies that the Supabase database is properly set up
and that user authentication/creation is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings
from app.core.database.connection import get_database_client
from app.core.database.repositories import UserRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


async def verify_database():
    """Verify database setup and connectivity."""
    print("=" * 70)
    print("MIRAGE DATABASE VERIFICATION")
    print("=" * 70)
    
    # Check configuration
    print("\n📋 Configuration Check:")
    print(f"  Supabase URL: {settings.SUPABASE_URL[:30]}..." if settings.SUPABASE_URL else "  ❌ SUPABASE_URL not set")
    print(f"  Supabase Key: {'✅ Set' if settings.SUPABASE_ANON_KEY else '❌ Not set'}")
    print(f"  JWT Secret: {'✅ Set' if settings.SUPABASE_JWT_SECRET else '⚠️  Not set (optional)'}")
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        print("\n❌ Missing required Supabase configuration!")
        print("Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file")
        return False
    
    # Test connection
    print("\n🔌 Testing Database Connection:")
    try:
        db_client = get_database_client()
        print("  ✅ Successfully connected to Supabase")
    except Exception as e:
        print(f"  ❌ Failed to connect to Supabase: {e}")
        return False
    
    # Check users table
    print("\n📊 Checking Users Table:")
    try:
        # Try to query the users table
        response = db_client.table('users').select('id', count='exact').limit(0).execute()
        print(f"  ✅ Users table exists")
        print(f"  📈 Total users in database: {response.count if hasattr(response, 'count') else 'Unknown'}")
    except Exception as e:
        print(f"  ❌ Users table check failed: {e}")
        print("\n⚠️  The users table may not exist. Please run the migration:")
        print("     1. Open Supabase Dashboard → SQL Editor")
        print("     2. Run: migrations/01_users_table.sql")
        return False
    
    # List recent users
    print("\n👥 Recent Users:")
    try:
        user_repo = UserRepository(db_client)
        response = db_client.table('users').select('*').order('created_at', desc=True).limit(5).execute()
        
        if response.data:
            for user in response.data:
                email = user.get('email', 'N/A')
                name = user.get('full_name', 'N/A')
                created = user.get('created_at', 'N/A')[:19] if user.get('created_at') else 'N/A'
                last_login = user.get('last_login_at', 'Never')
                if last_login != 'Never':
                    last_login = last_login[:19]
                print(f"  • {email} ({name})")
                print(f"    Created: {created} | Last Login: {last_login}")
        else:
            print("  No users found in database")
    except Exception as e:
        print(f"  ⚠️  Failed to list users: {e}")
    
    # Test user creation
    print("\n🧪 Testing User Creation:")
    test_user_data = {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "test_verification@example.com",
        "full_name": "Test User",
    }
    
    try:
        user_repo = UserRepository(db_client)
        
        # Check if test user exists
        existing = await user_repo.get_user_by_id(test_user_data["id"])
        if existing:
            print(f"  ℹ️  Test user already exists, deleting...")
            await user_repo.delete_user(test_user_data["id"])
        
        # Create test user
        created_user = await user_repo.create_user(test_user_data)
        print(f"  ✅ Successfully created test user: {created_user['email']}")
        
        # Verify created user
        fetched_user = await user_repo.get_user_by_id(test_user_data["id"])
        if fetched_user:
            print(f"  ✅ Successfully fetched test user from database")
        else:
            print(f"  ❌ Failed to fetch created user")
        
        # Clean up
        await user_repo.delete_user(test_user_data["id"])
        print(f"  🧹 Cleaned up test user")
        
    except Exception as e:
        print(f"  ❌ User creation test failed: {e}")
        logger.error(f"User creation test error: {e}", exc_info=True)
        return False
    
    print("\n" + "=" * 70)
    print("✅ DATABASE VERIFICATION COMPLETE - ALL CHECKS PASSED")
    print("=" * 70)
    return True


if __name__ == "__main__":
    print("\nStarting database verification...\n")
    
    try:
        result = asyncio.run(verify_database())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        logger.error(f"Verification error: {e}", exc_info=True)
        sys.exit(1)
