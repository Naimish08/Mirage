import asyncio
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"Loading env from: {env_path}")
load_dotenv(env_path)

# config.py logic might be better, but let's keep it simple and standalone
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer ANON key as SERVICE_KEY appears to be a UUID in this env
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_ANON_KEY) must be set in .env")
    sys.exit(1)

async def main():
    print(f"Connecting to Supabase at {SUPABASE_URL}...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    email = "temp_user@mirage.com"
    password = "temp_password_123!"
    
    print(f"Attempting to sign in user: {email}")
    
    try:
        # Try to sign in
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        print("✅ Sign in successful!")
        
    except Exception as e:
        print(f"Sign in failed. Attempting to sign up... Error: {e}")
        try:
            # Try to sign up
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": "Mirage Tester"
                    }
                }
            })
            print("Sign up successful!")
            
            # If email confirmation is enabled, this might fail to let us login immediately 
            # unless we use the returned session (if present) or if it's auto-confirmed.
            
        except Exception as signup_error:
            print(f"Sign up failed: {signup_error}")
            return

    if response.session:
        print("\n" + "="*60)
        print("ACCESS TOKEN (Save this!):")
        print("="*60)
        print(response.session.access_token)
        print("="*60 + "\n")
        print(f"User ID: {response.user.id}")
        
        # Verify creating a user record in our DB if needed via API, 
        # but the backend dependency should handle auto-creation on first request.
        
    else:
        print("⚠️ No session returned. User might need email confirmation.")

if __name__ == "__main__":
    asyncio.run(main())
