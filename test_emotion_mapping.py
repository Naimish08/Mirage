#!/usr/bin/env python
"""
Test script for emotional mapping components.
"""

import sys
import os
import asyncio

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

print("=" * 60)
print("🧪 Emotional Mapping Component Tests")
print("=" * 60)

async def test_emotion_detector():
    """Test the emotion detector with rate limiting."""
    print("\n1️⃣  Testing Emotion Detector...")
    try:
        from emotion.detector import EmotionDetector
        
        detector = EmotionDetector(min_analysis_interval=1)
        
        # Test with neutral (no API call needed)
        result = await detector.detect_emotion("Hello there")
        print(f"   ✅ Detector initialized")
        print(f"   - Emotion: {result['emotion']}")
        print(f"   - Confidence: {result['confidence']:.2f}")
        
        # Check stats
        stats = detector.get_stats()
        print(f"   - Rate limit: {stats['rate_limit']['calls_made']}/{stats['rate_limit']['max_calls']} calls")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_personality_adapter():
    """Test the personality adapter."""
    print("\n2️⃣  Testing Personality Adapter...")
    try:
        from emotion.personality_adapter import PersonalityAdapter
        
        adapter = PersonalityAdapter("teacher")
        
        # Test adaptation
        base_instructions = "You are a helpful teacher."
        emotion_data = {
            "emotion": "confused",
            "confidence": 0.8,
            "intensity": 0.6,
            "valence": -0.3,
            "arousal": 0.5,
            "detected_at": "2026-01-15T04:00:00Z"
        }
        
        adapted = adapter.adapt_instructions(base_instructions, emotion_data)
        
        print(f"   ✅ Adapter initialized")
        print(f"   - Agent type: teacher")
        print(f"   - Test emotion: confused")
        print(f"   - Instructions adapted: {len(adapted) > len(base_instructions)}")
        print(f"   - Contains guidance: {'confused' in adapted.lower()}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_session_handler():
    """Test the session handler."""
    print("\n3️⃣  Testing Session Handler...")
    try:
        from emotion.session_handler import EmotionAwareSessionHandler
        
        # Mock session object
        class MockSession:
            def on(self, event):
                def decorator(func):
                    return func
                return decorator
        
        handler = EmotionAwareSessionHandler(
            session=MockSession(),
            agent_type="teacher",
            session_id=None,
            auth_token=None
        )
        
        print(f"   ✅ Handler initialized")
        print(f"   - Agent type: teacher")
        print(f"   - Detector ready: {handler.detector is not None}")
        print(f"   - Adapter ready: {handler.adapter is not None}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_backend_service():
    """Test the backend emotion service."""
    print("\n4️⃣  Testing Backend Emotion Service...")
    try:
        from app.services.emotion_service import get_emotion_service
        
        service = get_emotion_service()
        
        # Test with simple text (will use fallback if quota exceeded)
        result = await service.analyze_text_sentiment("I am happy")
        
        print(f"   ✅ Service initialized")
        print(f"   - Emotion: {result['emotion']}")
        print(f"   - Confidence: {result['confidence']:.2f}")
        print(f"   - Valence: {result['valence']:.2f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_worker_syntax():
    """Test worker syntax."""
    print("\n5️⃣  Testing Worker Syntax...")
    try:
        import py_compile
        worker_path = os.path.join(os.path.dirname(__file__), 'agent', 'worker.py')
        py_compile.compile(worker_path, doraise=True)
        
        print(f"   ✅ Worker syntax valid")
        print(f"   - File: agent/worker.py")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def main():
    """Run all tests."""
    results = []
    
    # Run tests
    results.append(await test_emotion_detector())
    results.append(await test_personality_adapter())
    results.append(await test_session_handler())
    results.append(await test_backend_service())
    results.append(await test_worker_syntax())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
