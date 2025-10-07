#!/usr/bin/env python3
"""
Test script to validate simple spreadsheet-style queries work correctly.
Specifically tests the coxModelCode lookup that was failing before.
"""

import sys
from csv_demo import build_vectorstore, build_chain

def test_simple_queries():
    """Test simple spreadsheet-style queries."""
    print("🧪 Testing simple spreadsheet queries...")

    # Initialize the RAG system
    print("   📚 Building vector store...")
    vectorstore = build_vectorstore()

    print("   🔗 Building RAG chain...")
    chain = build_chain(vectorstore)

    # Test queries for simple CSV field lookups
    test_queries = [
        {
            "query": "What's the coxModelCode for the acura integra type s?",
            "expected_answer": "INTEG",
            "description": "Cox Model Code lookup (the original failing case)"
        },
        {
            "query": "What's the Cox make code for Bentley Continental GT?",
            "expected_answer": "BENTL",
            "description": "Cox Make Code lookup"
        },
        {
            "query": "What Cox model code does BMW M5 Touring have?",
            "expected_answer": "M5",
            "description": "Another Cox Model Code test"
        },
        {
            "query": "What's the Cox series name for Ferrari 308 GTS?",
            "expected_answer": "Should find series info",
            "description": "Cox Series lookup"
        }
    ]

    print(f"\n📝 Running {len(test_queries)} test queries:\n")

    results = []
    for i, test in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {test['description']}")
        print(f"   Query: {test['query']}")

        try:
            response = chain.invoke(test['query'])
            results.append({
                'test': test,
                'response': response,
                'success': test.get('expected_answer', '').upper() in response.upper() if test.get('expected_answer') != "Should find series info" else len(response) > 50
            })

            print(f"   Response: {response}")

            # Check if expected answer is found
            if test.get('expected_answer') and test['expected_answer'] != "Should find series info":
                found = test['expected_answer'].upper() in response.upper()
                print(f"   ✅ Expected '{test['expected_answer']}' found: {found}")
            else:
                print(f"   📝 Response length: {len(response)} chars")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                'test': test,
                'response': f"ERROR: {str(e)}",
                'success': False
            })

        print("-" * 60)

    # Summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)

    print(f"Successful tests: {successful_tests}/{total_tests}")

    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  Test {i}: {status} - {result['test']['description']}")

        if not result['success']:
            print(f"    Expected to find: {result['test'].get('expected_answer', 'N/A')}")
            print(f"    Actual response: {result['response'][:100]}...")

    return successful_tests == total_tests

if __name__ == "__main__":
    try:
        all_passed = test_simple_queries()

        print(f"\n🏁 FINAL RESULT")
        print("=" * 50)
        if all_passed:
            print("✅ SUCCESS: All simple spreadsheet queries work correctly!")
            print("The coxModelCode issue has been resolved.")
        else:
            print("⚠️ Some tests failed. Check the results above.")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        print("   Make sure Ollama is running and dependencies are installed")
        sys.exit(1)
