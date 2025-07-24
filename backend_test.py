#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Interview Copilot
Tests all backend endpoints with realistic interview scenarios
"""

import requests
import json
import time
from datetime import datetime
import sys

# Backend URL from frontend/.env
BACKEND_URL = "https://f581555b-dca5-41e2-b7a5-b4ee9f25f8c2.preview.emergentagent.com/api"

class InterviewCopilotTester:
    def __init__(self):
        self.session_id = None
        self.test_results = {
            "session_management": {"passed": 0, "failed": 0, "errors": []},
            "transcript_management": {"passed": 0, "failed": 0, "errors": []},
            "ai_integration": {"passed": 0, "failed": 0, "errors": []},
            "error_handling": {"passed": 0, "failed": 0, "errors": []}
        }
    
    def log_result(self, category, test_name, success, error_msg=None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[category]["failed"] += 1
            self.test_results[category]["errors"].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")
    
    def test_session_management(self):
        """Test interview session management endpoints"""
        print("\n🔍 Testing Session Management APIs...")
        
        # Test 1: Create new session
        try:
            response = requests.post(f"{BACKEND_URL}/interview/session", json={})
            if response.status_code == 200:
                session_data = response.json()
                self.session_id = session_data["id"]
                if "id" in session_data and "created_at" in session_data and session_data["is_active"]:
                    self.log_result("session_management", "Create new session", True)
                else:
                    self.log_result("session_management", "Create new session", False, "Missing required fields in response")
            else:
                self.log_result("session_management", "Create new session", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("session_management", "Create new session", False, str(e))
        
        # Test 2: Get specific session
        if self.session_id:
            try:
                response = requests.get(f"{BACKEND_URL}/interview/session/{self.session_id}")
                if response.status_code == 200:
                    session_data = response.json()
                    if session_data["id"] == self.session_id:
                        self.log_result("session_management", "Get specific session", True)
                    else:
                        self.log_result("session_management", "Get specific session", False, "Session ID mismatch")
                else:
                    self.log_result("session_management", "Get specific session", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("session_management", "Get specific session", False, str(e))
        
        # Test 3: Get all sessions
        try:
            response = requests.get(f"{BACKEND_URL}/interview/sessions")
            if response.status_code == 200:
                sessions = response.json()
                if isinstance(sessions, list) and len(sessions) > 0:
                    self.log_result("session_management", "Get all sessions", True)
                else:
                    self.log_result("session_management", "Get all sessions", False, "No sessions returned or invalid format")
            else:
                self.log_result("session_management", "Get all sessions", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("session_management", "Get all sessions", False, str(e))
    
    def test_transcript_management(self):
        """Test transcript management endpoints"""
        print("\n🔍 Testing Transcript Management APIs...")
        
        if not self.session_id:
            self.log_result("transcript_management", "All transcript tests", False, "No valid session ID available")
            return
        
        # Realistic interview transcript data
        transcript_entries = [
            {"session_id": self.session_id, "text": "Tell me about yourself and your background in software development.", "speaker": "interviewer"},
            {"session_id": self.session_id, "text": "I have 5 years of experience in full-stack development, primarily working with Python and React.", "speaker": "user"},
            {"session_id": self.session_id, "text": "What's your experience with database design and optimization?", "speaker": "interviewer"},
            {"session_id": self.session_id, "text": "I've worked extensively with both SQL and NoSQL databases, including PostgreSQL and MongoDB.", "speaker": "user"}
        ]
        
        # Test 1: Add transcript entries
        added_transcripts = []
        for i, entry in enumerate(transcript_entries):
            try:
                response = requests.post(f"{BACKEND_URL}/interview/transcript", json=entry)
                if response.status_code == 200:
                    transcript_data = response.json()
                    if "id" in transcript_data and transcript_data["session_id"] == self.session_id:
                        added_transcripts.append(transcript_data)
                        self.log_result("transcript_management", f"Add transcript entry {i+1}", True)
                    else:
                        self.log_result("transcript_management", f"Add transcript entry {i+1}", False, "Invalid transcript data returned")
                else:
                    self.log_result("transcript_management", f"Add transcript entry {i+1}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("transcript_management", f"Add transcript entry {i+1}", False, str(e))
        
        # Test 2: Get session transcripts
        try:
            response = requests.get(f"{BACKEND_URL}/interview/transcript/{self.session_id}")
            if response.status_code == 200:
                transcripts = response.json()
                if isinstance(transcripts, list) and len(transcripts) >= len(added_transcripts):
                    # Verify transcript order and content
                    if len(transcripts) > 0 and "timestamp" in transcripts[0]:
                        self.log_result("transcript_management", "Get session transcripts", True)
                    else:
                        self.log_result("transcript_management", "Get session transcripts", False, "Missing timestamp in transcripts")
                else:
                    self.log_result("transcript_management", "Get session transcripts", False, f"Expected at least {len(added_transcripts)} transcripts, got {len(transcripts) if isinstance(transcripts, list) else 0}")
            else:
                self.log_result("transcript_management", "Get session transcripts", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("transcript_management", "Get session transcripts", False, str(e))
    
    def test_ai_integration(self):
        """Test Gemini AI integration and response generation"""
        print("\n🔍 Testing AI Integration and Response Generation...")
        
        if not self.session_id:
            self.log_result("ai_integration", "All AI tests", False, "No valid session ID available")
            return
        
        # Test realistic interview questions
        test_questions = [
            "What are your greatest strengths as a software developer?",
            "Describe a challenging project you worked on and how you overcame obstacles.",
            "How do you stay updated with the latest technology trends?"
        ]
        
        for i, question in enumerate(test_questions):
            try:
                print(f"  Testing AI response for question {i+1}...")
                response = requests.post(
                    f"{BACKEND_URL}/interview/ai-response",
                    json={"session_id": self.session_id, "question": question},
                    timeout=30  # AI responses may take time
                )
                
                if response.status_code == 200:
                    ai_data = response.json()
                    if all(key in ai_data for key in ["id", "session_id", "question", "response", "timestamp"]):
                        if ai_data["session_id"] == self.session_id and ai_data["question"] == question:
                            if len(ai_data["response"]) > 50:  # Ensure substantial response
                                self.log_result("ai_integration", f"AI response generation {i+1}", True)
                                print(f"    Response preview: {ai_data['response'][:100]}...")
                            else:
                                self.log_result("ai_integration", f"AI response generation {i+1}", False, "Response too short")
                        else:
                            self.log_result("ai_integration", f"AI response generation {i+1}", False, "Session ID or question mismatch")
                    else:
                        self.log_result("ai_integration", f"AI response generation {i+1}", False, "Missing required fields in AI response")
                else:
                    self.log_result("ai_integration", f"AI response generation {i+1}", False, f"HTTP {response.status_code}: {response.text}")
                
                # Add delay between AI requests to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                self.log_result("ai_integration", f"AI response generation {i+1}", False, str(e))
        
        # Test: Get AI responses for session
        try:
            response = requests.get(f"{BACKEND_URL}/interview/ai-responses/{self.session_id}")
            if response.status_code == 200:
                ai_responses = response.json()
                if isinstance(ai_responses, list) and len(ai_responses) > 0:
                    self.log_result("ai_integration", "Get session AI responses", True)
                else:
                    self.log_result("ai_integration", "Get session AI responses", False, "No AI responses found")
            else:
                self.log_result("ai_integration", "Get session AI responses", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("ai_integration", "Get session AI responses", False, str(e))
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🔍 Testing Error Handling...")
        
        # Test 1: Get non-existent session
        try:
            response = requests.get(f"{BACKEND_URL}/interview/session/non-existent-id")
            if response.status_code == 404:
                self.log_result("error_handling", "Non-existent session returns 404", True)
            else:
                self.log_result("error_handling", "Non-existent session returns 404", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Non-existent session returns 404", False, str(e))
        
        # Test 2: Add transcript to non-existent session
        try:
            response = requests.post(
                f"{BACKEND_URL}/interview/transcript",
                json={"session_id": "non-existent-id", "text": "Test transcript", "speaker": "interviewer"}
            )
            if response.status_code == 404:
                self.log_result("error_handling", "Transcript for non-existent session returns 404", True)
            else:
                self.log_result("error_handling", "Transcript for non-existent session returns 404", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Transcript for non-existent session returns 404", False, str(e))
        
        # Test 3: AI response for non-existent session
        try:
            response = requests.post(
                f"{BACKEND_URL}/interview/ai-response",
                json={"session_id": "non-existent-id", "question": "Test question"}
            )
            if response.status_code == 404:
                self.log_result("error_handling", "AI response for non-existent session returns 404", True)
            else:
                self.log_result("error_handling", "AI response for non-existent session returns 404", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "AI response for non-existent session returns 404", False, str(e))
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n🔍 Testing Basic API Connectivity...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    print("✅ Basic API connectivity successful")
                    return True
                else:
                    print("❌ Basic API connectivity: Invalid response format")
                    return False
            else:
                print(f"❌ Basic API connectivity: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Basic API connectivity failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Interview Copilot Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("\n❌ Basic connectivity failed. Aborting tests.")
            return False
        
        # Run all test suites
        self.test_session_management()
        self.test_transcript_management()
        self.test_ai_integration()
        self.test_error_handling()
        
        # Print summary
        self.print_summary()
        
        return self.is_overall_success()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.replace('_', ' ').title()}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  - {error}")
        
        print("-" * 60)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL: {overall_status} ({total_passed} passed, {total_failed} failed)")
        print("=" * 60)
    
    def is_overall_success(self):
        """Check if all tests passed"""
        return sum(results["failed"] for results in self.test_results.values()) == 0

if __name__ == "__main__":
    tester = InterviewCopilotTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)