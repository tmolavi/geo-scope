import json
from pathlib import Path

# 50 Countries across 6 regions
COUNTRIES = [
    # 1. MENA (10)
    ("Iran", "IRN", "middle_east_north_africa", "fa"),
    ("Turkey", "TUR", "middle_east_north_africa", "tr"),
    ("Saudi Arabia", "SAU", "middle_east_north_africa", "ar"),
    ("United Arab Emirates", "ARE", "middle_east_north_africa", "ar"),
    ("Yemen", "YEM", "middle_east_north_africa", "ar"),
    ("Egypt", "EGY", "middle_east_north_africa", "ar"),
    ("Morocco", "MAR", "middle_east_north_africa", "ar"),
    ("Iraq", "IRQ", "middle_east_north_africa", "ar"),
    ("Jordan", "JOR", "middle_east_north_africa", "ar"),
    ("Qatar", "QAT", "middle_east_north_africa", "ar"),
    # 2. North America (3)
    ("United States", "USA", "north_america", "en"),
    ("Canada", "CAN", "north_america", "en"),
    ("Mexico", "MEX", "north_america", "es"),
    # 3. Europe (15)
    ("Germany", "DEU", "europe", "de"),
    ("United Kingdom", "GBR", "europe", "en"),
    ("France", "FRA", "europe", "fr"),
    ("Italy", "ITA", "europe", "it"),
    ("Spain", "ESP", "europe", "es"),
    ("Netherlands", "NLD", "europe", "nl"),
    ("Sweden", "SWE", "europe", "sv"),
    ("Poland", "POL", "europe", "pl"),
    ("Switzerland", "CHE", "europe", "de"),
    ("Austria", "AUT", "europe", "de"),
    ("Belgium", "BEL", "europe", "nl"),
    ("Ireland", "IRL", "europe", "en"),
    ("Norway", "NOR", "europe", "no"),
    ("Denmark", "DNK", "europe", "da"),
    ("Finland", "FIN", "europe", "fi"),
    # 4. Asia Pacific (12)
    ("India", "IND", "asia_pacific", "hi"),
    ("China", "CHN", "asia_pacific", "zh"),
    ("Japan", "JPN", "asia_pacific", "ja"),
    ("South Korea", "KOR", "asia_pacific", "ko"),
    ("Indonesia", "IDN", "asia_pacific", "id"),
    ("Pakistan", "PAK", "asia_pacific", "ur"),
    ("Vietnam", "VNM", "asia_pacific", "vi"),
    ("Philippines", "PHL", "asia_pacific", "tl"),
    ("Australia", "AUS", "asia_pacific", "en"),
    ("Singapore", "SGP", "asia_pacific", "en"),
    ("New Zealand", "NZL", "asia_pacific", "en"),
    ("Malaysia", "MYS", "asia_pacific", "ms"),
    # 5. Latin America (5)
    ("Brazil", "BRA", "latin_america", "pt"),
    ("Argentina", "ARG", "latin_america", "es"),
    ("Colombia", "COL", "latin_america", "es"),
    ("Chile", "CHL", "latin_america", "es"),
    ("Peru", "PER", "latin_america", "es"),
    # 6. Sub-Saharan Africa (5)
    ("Nigeria", "NGA", "sub_saharan_africa", "en"),
    ("South Africa", "ZAF", "sub_saharan_africa", "en"),
    ("Kenya", "KEN", "sub_saharan_africa", "sw"),
    ("Ghana", "GHA", "sub_saharan_africa", "en"),
    ("Ethiopia", "ETH", "sub_saharan_africa", "am"),
]

CATEGORIES = [
    "future_skills_learning",
    "career_migration",
    "entrepreneurship_business",
    "ai_adoption",
    "technology_impact",
    "health_lifestyle",
    "education_choices",
    "financial_decisions",
    "creativity_culture",
]

print(f"Total Countries: {len(COUNTRIES)}")
print(f"Total Categories: {len(CATEGORIES)}")
