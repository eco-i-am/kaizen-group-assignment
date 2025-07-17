#!/usr/bin/env python3

from group_assignment_to_excel import get_timezone_region, extract_country_from_field

def test_country_extraction():
    print("Testing country extraction:")
    test_cases = [
        "Abu Dhabi, United Arab Emirates",
        "Ras Al Khaimah, United Arab Emirates",
        "Dubai, UAE",
        "Bermuda",
        "Cayman Islands",
        "nan, Cayman Islands",
        "North America, Bermuda"
    ]
    
    for test_case in test_cases:
        extracted = extract_country_from_field(test_case)
        timezone = get_timezone_region(test_case)
        print(f"{test_case} -> {extracted} -> {timezone}")

if __name__ == "__main__":
    test_country_extraction() 