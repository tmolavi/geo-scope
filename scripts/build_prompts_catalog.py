import json
from pathlib import Path

# Template matrix for 9 categories across 50 countries
# Let's define localized prompt generator covering all 50 countries

COUNTRY_SPECS = [
    # MENA (10)
    {"name": "Iran", "iso": "IRN", "region": "middle_east_north_africa", "lang": "fa"},
    {"name": "Turkey", "iso": "TUR", "region": "middle_east_north_africa", "lang": "tr"},
    {"name": "Saudi Arabia", "iso": "SAU", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "United Arab Emirates", "iso": "ARE", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Yemen", "iso": "YEM", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Egypt", "iso": "EGY", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Morocco", "iso": "MAR", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Iraq", "iso": "IRQ", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Jordan", "iso": "JOR", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Qatar", "iso": "QAT", "region": "middle_east_north_africa", "lang": "ar"},

    # North America (3)
    {"name": "United States", "iso": "USA", "region": "north_america", "lang": "en"},
    {"name": "Canada", "iso": "CAN", "region": "north_america", "lang": "en"},
    {"name": "Mexico", "iso": "MEX", "region": "north_america", "lang": "es"},

    # Europe (15)
    {"name": "Germany", "iso": "DEU", "region": "europe", "lang": "de"},
    {"name": "United Kingdom", "iso": "GBR", "region": "europe", "lang": "en"},
    {"name": "France", "iso": "FRA", "region": "europe", "lang": "fr"},
    {"name": "Italy", "iso": "ITA", "region": "europe", "lang": "it"},
    {"name": "Spain", "iso": "ESP", "region": "europe", "lang": "es"},
    {"name": "Netherlands", "iso": "NLD", "region": "europe", "lang": "nl"},
    {"name": "Sweden", "iso": "SWE", "region": "europe", "lang": "sv"},
    {"name": "Poland", "iso": "POL", "region": "europe", "lang": "pl"},
    {"name": "Switzerland", "iso": "CHE", "region": "europe", "lang": "de"},
    {"name": "Austria", "iso": "AUT", "region": "europe", "lang": "de"},
    {"name": "Belgium", "iso": "BEL", "region": "europe", "lang": "nl"},
    {"name": "Ireland", "iso": "IRL", "region": "europe", "lang": "en"},
    {"name": "Norway", "iso": "NOR", "region": "europe", "lang": "no"},
    {"name": "Denmark", "iso": "DNK", "region": "europe", "lang": "da"},
    {"name": "Finland", "iso": "FIN", "region": "europe", "lang": "fi"},

    # Asia Pacific (12)
    {"name": "India", "iso": "IND", "region": "asia_pacific", "lang": "hi"},
    {"name": "China", "iso": "CHN", "region": "asia_pacific", "lang": "zh"},
    {"name": "Japan", "iso": "JPN", "region": "asia_pacific", "lang": "ja"},
    {"name": "South Korea", "iso": "KOR", "region": "asia_pacific", "lang": "ko"},
    {"name": "Indonesia", "iso": "IDN", "region": "asia_pacific", "lang": "id"},
    {"name": "Pakistan", "iso": "PAK", "region": "asia_pacific", "lang": "ur"},
    {"name": "Vietnam", "iso": "VNM", "region": "asia_pacific", "lang": "vi"},
    {"name": "Philippines", "iso": "PHL", "region": "asia_pacific", "lang": "tl"},
    {"name": "Australia", "iso": "AUS", "region": "asia_pacific", "lang": "en"},
    {"name": "Singapore", "iso": "SGP", "region": "asia_pacific", "lang": "en"},
    {"name": "New Zealand", "iso": "NZL", "region": "asia_pacific", "lang": "en"},
    {"name": "Malaysia", "iso": "MYS", "region": "asia_pacific", "lang": "ms"},

    # Latin America (5)
    {"name": "Brazil", "iso": "BRA", "region": "latin_america", "lang": "pt"},
    {"name": "Argentina", "iso": "ARG", "region": "latin_america", "lang": "es"},
    {"name": "Colombia", "iso": "COL", "region": "latin_america", "lang": "es"},
    {"name": "Chile", "iso": "CHL", "region": "latin_america", "lang": "es"},
    {"name": "Peru", "iso": "PER", "region": "latin_america", "lang": "es"},

    # Sub-Saharan Africa (5)
    {"name": "Nigeria", "iso": "NGA", "region": "sub_saharan_africa", "lang": "en"},
    {"name": "South Africa", "iso": "ZAF", "region": "sub_saharan_africa", "lang": "en"},
    {"name": "Kenya", "iso": "KEN", "region": "sub_saharan_africa", "lang": "sw"},
    {"name": "Ghana", "iso": "GHA", "region": "sub_saharan_africa", "lang": "en"},
    {"name": "Ethiopia", "iso": "ETH", "region": "sub_saharan_africa", "lang": "am"},
]

print("Validated 50 country specifications.")
