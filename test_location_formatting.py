#!/usr/bin/env python3
"""
Test script to verify location formatting logic
"""

def format_location_display(member, column_mapping):
    """Format location display based on residing_ph status"""
    residing_ph = str(member.get(column_mapping.get('residing_ph'), '0')).strip().lower()
    
    if residing_ph in ['1', '1.0', 'true', 'yes', 'ph', 'philippines']:
        # Philippines resident - show "city, province" format
        city = member.get(column_mapping.get('city'), '')
        province = member.get(column_mapping.get('province'), '')
        
        # Use "MM" as acronym for Metro Manila
        if province and province.lower() == 'metro manila':
            province = 'MM'
        
        if city and province:
            return f"{city}, {province}"
        elif city:
            return city
        elif province:
            return province
        else:
            return ''
    else:
        # International resident - show "State, Country"
        state = member.get(column_mapping.get('state'), '')
        country = member.get(column_mapping.get('country'), '')
        if state and country:
            return f"{state}, {country}"
        elif country:
            return country
        else:
            return member.get(column_mapping.get('city'), '')

def test_location_formatting():
    """Test the location formatting logic"""
    
    # Sample column mapping
    column_mapping = {
        'residing_ph': 'residing_ph',
        'city': 'city',
        'province': 'province',
        'state': 'state',
        'country': 'country'
    }
    
    # Test cases
    test_cases = [
        {
            'name': 'Philippines - Metro Manila with city',
            'member': {
                'residing_ph': '1',
                'city': 'Quezon City',
                'province': 'Metro Manila',
                'state': '',
                'country': 'Philippines'
            },
            'expected': 'Quezon City, MM'
        },
        {
            'name': 'Philippines - Metro Manila without city',
            'member': {
                'residing_ph': '1',
                'city': '',
                'province': 'Metro Manila',
                'state': '',
                'country': 'Philippines'
            },
            'expected': 'MM'
        },
        {
            'name': 'Philippines - Other province with city',
            'member': {
                'residing_ph': '1',
                'city': 'Cebu City',
                'province': 'Cebu',
                'state': '',
                'country': 'Philippines'
            },
            'expected': 'Cebu City, Cebu'
        },
        {
            'name': 'Philippines - Other province without city',
            'member': {
                'residing_ph': '1',
                'city': '',
                'province': 'Batangas',
                'state': '',
                'country': 'Philippines'
            },
            'expected': 'Batangas'
        },
        {
            'name': 'Philippines - Only city',
            'member': {
                'residing_ph': '1',
                'city': 'Manila',
                'province': '',
                'state': '',
                'country': 'Philippines'
            },
            'expected': 'Manila'
        },
        {
            'name': 'International - State and Country',
            'member': {
                'residing_ph': '0',
                'city': 'Los Angeles',
                'province': '',
                'state': 'California',
                'country': 'United States'
            },
            'expected': 'California, United States'
        },
        {
            'name': 'International - Only Country',
            'member': {
                'residing_ph': '0',
                'city': 'Toronto',
                'province': '',
                'state': '',
                'country': 'Canada'
            },
            'expected': 'Canada'
        },
        {
            'name': 'International - Only City',
            'member': {
                'residing_ph': '0',
                'city': 'Singapore',
                'province': '',
                'state': '',
                'country': ''
            },
            'expected': 'Singapore'
        },
        {
            'name': 'Philippines - Case insensitive Metro Manila',
            'member': {
                'residing_ph': '1',
                'city': 'Makati',
                'province': 'metro manila',
                'state': '',
                'country': 'Philippines'
            },
            'expected': 'Makati, MM'
        },
        {
            'name': 'Philippines - Mixed case Metro Manila',
            'member': {
                'residing_ph': '1',
                'city': 'Taguig',
                'province': 'Metro Manila',
                'state': '',
                'country': 'Philippines'
            },
            'expected': 'Taguig, MM'
        }
    ]
    
    print("Testing location formatting logic:")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        result = format_location_display(test_case['member'], column_mapping)
        expected = test_case['expected']
        
        if result == expected:
            print(f"✅ PASS: {test_case['name']}")
            print(f"   Result: '{result}'")
            passed += 1
        else:
            print(f"❌ FAIL: {test_case['name']}")
            print(f"   Expected: '{expected}'")
            print(f"   Got: '{result}'")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")

if __name__ == "__main__":
    test_location_formatting() 