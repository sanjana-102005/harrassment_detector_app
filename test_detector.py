"""
Comprehensive test suite for the Harassment Detection System.
Tests rule-based detection, ML classification, and integrated analysis.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from detector import HarassmentDetector
import json

def print_result(test_name: str, result: dict, expected_category: str = None):
    """Pretty print test results."""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)
    print(f"Input: {result.get('input_text', 'N/A')[:100]}...")
    print(f"\nClassification: {'HARASSMENT' if result['is_harassment'] else 'NON-HARASSMENT'}")
    print(f"Category: {result['category']}")
    print(f"Severity: {result['severity']}")
    print(f"Confidence: {result['confidence_score']:.2%}")
    print(f"\nExplanation: {result['explanation']}")
    
    if result['indicators']:
        print("\nIndicators:")
        for ind in result['indicators']:
            print(f"  • {ind}")
    
    if expected_category:
        match = "✓ PASS" if expected_category.lower() in result['category'].lower() else "✗ FAIL"
        print(f"\nExpected: {expected_category} | Result: {match}")
    
    print("="*80)

def run_tests():
    """Run comprehensive test suite."""
    
    print("\n" + "🧪"*40)
    print("HARASSMENT DETECTION SYSTEM - TEST SUITE")
    print("🧪"*40 + "\n")
    
    detector = HarassmentDetector()
    
    # Test cases organized by category
    test_cases = [
        # SEXUAL HARASSMENT - High Severity
        {
            'name': 'Sexual Harassment - Explicit Assault',
            'text': 'My boss cornered me in the office and tried to touch me inappropriately. He said if I want the promotion, I need to be "friendly" with him. This has happened multiple times despite me saying no.',
            'expected': 'Sexual Harassment',
            'expected_harassment': True
        },
        {
            'name': 'Sexual Harassment - Repeated Advances',
            'text': 'A colleague keeps sending me explicit messages late at night. I have told him to stop many times but he continues. Yesterday he sent me nude photos without my consent.',
            'expected': 'Sexual Harassment',
            'expected_harassment': True
        },
        
        # THREATS - High Severity
        {
            'name': 'Threats - Direct Violence',
            'text': 'Someone sent me messages saying they will hurt me and my family if I don\'t do what they say. They know where I live and said they will come after me.',
            'expected': 'Threat',
            'expected_harassment': True
        },
        {
            'name': 'Threats - Blackmail',
            'text': 'My ex-partner is threatening to leak my private photos online if I don\'t get back together with them. They keep warning me about consequences.',
            'expected': 'Threat',
            'expected_harassment': True
        },
        
        # PHYSICAL HARASSMENT
        {
            'name': 'Physical Harassment - Assault',
            'text': 'During an argument, my roommate pushed me against the wall and slapped me. They have done this before when angry.',
            'expected': 'Physical',
            'expected_harassment': True
        },
        {
            'name': 'Physical Harassment - Unwanted Contact',
            'text': 'A stranger on the bus keeps touching me without permission. When I asked them to stop, they just laughed and moved closer to me.',
            'expected': 'Physical',
            'expected_harassment': True
        },
        
        # CYBER HARASSMENT
        {
            'name': 'Cyber Harassment - Doxxing',
            'text': 'Someone posted my personal address, phone number, and workplace information on social media along with hateful comments. I\'m receiving hundreds of threatening messages now.',
            'expected': 'Cyber',
            'expected_harassment': True
        },
        {
            'name': 'Cyber Harassment - Impersonation',
            'text': 'Someone created a fake profile using my photos and is sending inappropriate messages to people pretending to be me. This is ruining my reputation.',
            'expected': 'Cyber',
            'expected_harassment': True
        },
        
        # STALKING
        {
            'name': 'Stalking - Following',
            'text': 'A person has been following me for the past three weeks. They show up everywhere I go - at work, the grocery store, even outside my home. Despite me telling them to leave me alone, they won\'t stop.',
            'expected': 'Stalking',
            'expected_harassment': True
        },
        {
            'name': 'Stalking - Surveillance',
            'text': 'Someone keeps monitoring my social media and knows my exact schedule. They leave notes at my door showing they know where I\'ve been. I feel constantly watched.',
            'expected': 'Stalking',
            'expected_harassment': True
        },
        
        # WORKPLACE HARASSMENT
        {
            'name': 'Workplace Harassment - Discrimination',
            'text': 'My manager constantly makes discriminatory comments about my gender and excludes me from important meetings. When I complained, I was passed over for a promotion I deserved.',
            'expected': 'Workplace',
            'expected_harassment': True
        },
        {
            'name': 'Workplace Harassment - Hostile Environment',
            'text': 'My colleagues create a hostile work environment by making sexual jokes, showing explicit content, and making me feel uncomfortable daily. HR has done nothing despite multiple complaints.',
            'expected': 'Workplace',
            'expected_harassment': True
        },
        
        # VERBAL HARASSMENT
        {
            'name': 'Verbal Harassment - Insults',
            'text': 'My neighbor constantly yells derogatory slurs at me and calls me offensive names. They do this in public and it happens almost every day.',
            'expected': 'Verbal',
            'expected_harassment': True
        },
        
        # NON-HARASSMENT CASES (Important for false positive testing)
        {
            'name': 'Non-Harassment - Work Disagreement',
            'text': 'My colleague and I had a disagreement about how to approach a project. They were firm in their opinion and we had a heated discussion, but it was professional.',
            'expected': 'Non-Harassment',
            'expected_harassment': False
        },
        {
            'name': 'Non-Harassment - Constructive Criticism',
            'text': 'My manager gave me critical feedback about my performance. While it was uncomfortable to hear, it was delivered professionally and focused on my work, not personal attacks.',
            'expected': 'Non-Harassment',
            'expected_harassment': False
        },
        {
            'name': 'Non-Harassment - Accidental Bump',
            'text': 'Someone accidentally bumped into me on the crowded train this morning. They apologized immediately and moved away.',
            'expected': 'Non-Harassment',
            'expected_harassment': False
        },
        {
            'name': 'Non-Harassment - Relationship Conflict',
            'text': 'My partner and I had an argument about household responsibilities. We both raised our voices but it was a normal couple disagreement.',
            'expected': 'Non-Harassment',
            'expected_harassment': False
        },
        {
            'name': 'Non-Harassment - Stress/Anxiety',
            'text': 'I feel anxious and stressed about my workload. There\'s a lot of pressure to meet deadlines and I\'m worried about my performance.',
            'expected': 'Non-Harassment',
            'expected_harassment': False
        },
        
        # EDGE CASES
        {
            'name': 'Edge Case - Ambiguous Situation',
            'text': 'Someone at work asked me out for coffee. I said no politely, and they said okay and walked away. I felt a bit uncomfortable but they haven\'t mentioned it again.',
            'expected': 'Non-Harassment',
            'expected_harassment': False
        },
        {
            'name': 'Edge Case - Repeated Contact (Non-threatening)',
            'text': 'An old friend keeps messaging me on social media trying to reconnect. I haven\'t responded but they message every few weeks asking how I\'m doing.',
            'expected': 'Non-Harassment',
            'expected_harassment': False
        },
        {
            'name': 'Edge Case - Boundary Violation',
            'text': 'Someone I know keeps showing up at events I attend even though I asked them for space. They try to talk to me each time despite me being clear about needing distance.',
            'expected': 'Stalking',
            'expected_harassment': True
        },
    ]
    
    # Run tests
    results = []
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        result = detector.analyze_incident(test_case['text'])
        result['input_text'] = test_case['text']
        
        print_result(
            test_case['name'],
            result,
            test_case.get('expected')
        )
        
        # Check if result matches expectation
        harassment_match = result['is_harassment'] == test_case.get('expected_harassment', True)
        category_match = test_case.get('expected', '').lower() in result['category'].lower()
        
        if harassment_match and (category_match or not test_case.get('expected_harassment')):
            passed += 1
            status = 'PASS'
        else:
            failed += 1
            status = 'FAIL'
        
        results.append({
            'test_name': test_case['name'],
            'status': status,
            'expected': test_case.get('expected'),
            'actual': result['category'],
            'confidence': result['confidence_score']
        })
    
    # Print summary
    print("\n\n" + "📊"*40)
    print("TEST SUMMARY")
    print("📊"*40)
    print(f"\nTotal Tests: {len(test_cases)}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    
    # Detailed results
    print("\n" + "-"*80)
    print("DETAILED RESULTS")
    print("-"*80)
    for r in results:
        status_symbol = "✓" if r['status'] == 'PASS' else "✗"
        print(f"{status_symbol} {r['test_name']}")
        print(f"   Expected: {r['expected']} | Actual: {r['actual']} | Confidence: {r['confidence']:.2%}")
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80 + "\n")
    
    return results

def test_specific_features():
    """Test specific features of the detector."""
    
    print("\n" + "🔧"*40)
    print("FEATURE-SPECIFIC TESTS")
    print("🔧"*40 + "\n")
    
    detector = HarassmentDetector()
    
    # Test 1: Multiple categories in one incident
    print("\n### Test: Multiple Category Detection ###")
    multi_category_text = "My boss keeps making sexual comments about my body and threatens to fire me if I complain. They also follow me around the office constantly."
    result = detector.analyze_incident(multi_category_text)
    print(f"Text: {multi_category_text}")
    print(f"Detected Categories: {result.get('category')}")
    print(f"Severity: {result['severity']}")
    print(f"Should be High/Critical: {'✓ PASS' if result['severity'] in ['High', 'Critical'] else '✗ FAIL'}")
    
    # Test 2: Intent pattern detection
    print("\n### Test: Intent Pattern Detection ###")
    intent_text = "I told them to stop messaging me but they won't listen. They keep contacting me despite me saying no clearly."
    result = detector.analyze_incident(intent_text)
    print(f"Text: {intent_text}")
    print(f"Indicators: {result['indicators']}")
    print(f"Should detect boundary violation: {'✓ PASS' if any('Pattern' in ind for ind in result['indicators']) else '✗ FAIL'}")
    
    # Test 3: Confidence scoring
    print("\n### Test: Confidence Scoring ###")
    high_confidence = "They grabbed me and forced me to do things against my will repeatedly."
    low_confidence = "Someone was a bit rude to me today."
    
    result_high = detector.analyze_incident(high_confidence)
    result_low = detector.analyze_incident(low_confidence)
    
    print(f"High confidence case: {result_high['confidence_score']:.2%}")
    print(f"Low confidence case: {result_low['confidence_score']:.2%}")
    print(f"Proper distinction: {'✓ PASS' if result_high['confidence_score'] > result_low['confidence_score'] else '✗ FAIL'}")
    
    # Test 4: Gender inclusivity
    print("\n### Test: Gender Inclusivity ###")
    test_texts = [
        "My male colleague was sexually harassed by his female boss.",
        "As a non-binary person, I faced discrimination at work.",
        "My husband was stalked by his ex-girlfriend.",
    ]
    
    for text in test_texts:
        result = detector.analyze_incident(text)
        print(f"\nText: {text}")
        print(f"Detected as harassment: {result['is_harassment']}")
        print(f"Category: {result['category']}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    # Run main test suite
    results = run_tests()
    
    # Run feature tests
    test_specific_features()
    
    print("\n✅ All tests completed successfully!\n")
