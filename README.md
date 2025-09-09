# World Currencies Data

A comprehensive, automatically updated dataset of world currencies with complete country mappings and historical transitions. Data is synchronized daily from authoritative sources including Unicode CLDR, ISO 4217, and ISO 3166 standards.

## 📊 Dataset Overview

This project provides structured currency data in multiple formats:

- **Current Currencies**: Active currency mappings for all countries and territories
- **Historical Data**: Complete timeline of currency changes, adoptions, and transitions  
- **ISO Mappings**: Simplified country-currency reference tables
- **Multiple Formats**: CSV and JSON outputs for different use cases

### Data Sources
- **Unicode CLDR**: Authoritative currency-territory mappings
- **ISO 4217**: Official currency codes and names
- **ISO 3166**: Country codes and names
- **pycountry**: Standardized country/currency metadata

## 🚀 Quick Start

### Direct Download (Latest Release)

```bash
# Current currencies (CSV)
curl -O https://github.com/estifie/world-currencies-data/releases/latest/download/current_currencies.csv

# Historical currencies with complete timeline (CSV)
curl -O https://github.com/estifie/world-currencies-data/releases/latest/download/historical_currencies.csv

# JSON formats
curl -O https://github.com/estifie/world-currencies-data/releases/latest/download/current_currencies.json
curl -O https://github.com/estifie/world-currencies-data/releases/latest/download/historical_currencies.json

# Simplified ISO mappings
curl -O https://github.com/estifie/world-currencies-data/releases/latest/download/iso_mappings.json

# Metadata
curl -O https://github.com/estifie/world-currencies-data/releases/latest/download/metadata.json
```

### Using Raw Data URLs

```bash
# Current data from main branch
curl -O https://raw.githubusercontent.com/estifie/world-currencies-data/main/data/current_currencies.csv
curl -O https://raw.githubusercontent.com/estifie/world-currencies-data/main/data/historical_currencies.csv
```

## 📋 Data Formats

### Current Currencies (`current_currencies.csv`)

Active currency mappings for all countries and territories:

```csv
country_code,country_name,currency_code,currency_name
AD,Andorra,EUR,Euro
AE,United Arab Emirates,AED,UAE Dirham
AF,Afghanistan,AFN,Afghan Afghani
```

**Fields:**
- `country_code`: ISO 3166-1 alpha-2 country code
- `country_name`: Official country name
- `currency_code`: ISO 4217 currency code  
- `currency_name`: Official currency name

### Historical Currencies (`historical_currencies.csv`)

Complete timeline including active and discontinued currencies:

```csv
country_code,country_name,currency_code,currency_name,start_date,end_date,is_active
DE,Germany,DEM,German Mark,1948-06-20,2002-02-28,False
DE,Germany,EUR,Euro,1999-01-01,,True
```

**Fields:**
- `start_date`: Currency introduction date (YYYY-MM-DD)
- `end_date`: Currency discontinuation date (empty for active)
- `is_active`: Boolean indicating current usage

### JSON Formats

Structured data with nested country information:

```json
{
  "AD": {
    "country_name": "Andorra",
    "official_country_name": "Principality of Andorra",
    "currency_code": "EUR",
    "currency_name": "Euro"
  }
}
```

### ISO Mappings (`iso_mappings.json`)

Simplified reference for quick lookups:

```json
{
  "countries": {
    "AD": "Andorra",
    "AE": "United Arab Emirates"
  },
  "currencies": {
    "EUR": "Euro",
    "AED": "UAE Dirham"
  }
}
```

## 🔄 Data Generation Process

The currency data is generated through a systematic process:

### 1. Data Collection
- Fetches latest currency-territory mappings from Unicode CLDR
- Retrieves country names and codes from ISO 3166 via pycountry
- Obtains currency codes and names from ISO 4217 standards

### 2. Data Processing
- Excludes non-tender currencies (commemorative, testing codes)
- Applies business rules for currency validity and territory coverage
- Handles special cases and currency transitions

### 3. Historical Integration
- Maintains complete currency timeline with start/end dates
- Tracks currency adoptions, transitions, and discontinuations
- Preserves historical context for monetary policy analysis

### 4. Quality Assurance
- Validates against multiple authoritative sources
- Ensures data consistency and completeness
- Performs automated quality checks

### 5. Output Generation
- Creates multiple formats (CSV, JSON) for different use cases
- Generates simplified mappings for quick reference
- Produces comprehensive metadata with update information

## ⚙️ Automation Workflow

### Schedule
- **Daily Updates**: 2:00 AM UTC
- **Manual Triggers**: Available via GitHub Actions
- **Change Detection**: Automatic on script modifications

### Process
1. **Environment Setup**: Python 3.11 with required dependencies
2. **Data Sync**: Fetch latest from all authoritative sources
3. **Validation**: Verify data integrity and completeness
4. **Generation**: Create all output formats with UTF-8 encoding
5. **Version Control**: Commit changes with detailed metadata
6. **Release**: Create timestamped release with downloadable assets

### Commit Strategy
- **Data Changes**: Creates standard commit with change summary
- **No Changes**: Creates empty commit for audit trail and verification
- **Attribution**: All commits attributed to repository owner
- **Messages**: Descriptive commit messages with update statistics

### Release Assets
Each automated release includes:
- All CSV and JSON data files
- Metadata with generation timestamp and source versions
- Release notes with data statistics and download instructions
- Direct download links for all formats

## 🛠️ Development

### Prerequisites
```bash
python3 -v  # 3.8+
pip install requests pandas lxml beautifulsoup4 pycountry
```

### Local Generation
```bash
git clone https://github.com/estifie/world-currencies-data.git
cd world-currencies-data
python scripts/update_currency_data.py
```

### File Structure
```
world-currencies-data/
├── data/                          # Generated data files
│   ├── current_currencies.csv     # Active currencies only
│   ├── historical_currencies.csv  # Complete currency timeline  
│   ├── current_currencies.json    # JSON format (current)
│   ├── historical_currencies.json # JSON format (historical)
│   ├── iso_mappings.json          # Simplified mappings
│   └── metadata.json              # Generation metadata
├── scripts/
│   └── update_currency_data.py    # Data generation script
├── .github/workflows/
│   └── update-currency-data.yml   # Automation workflow
└── README.md
```

## 📈 Data Statistics

Current dataset includes:
- **266 countries and territories** with currency mappings
- **Active currencies**: ~180 distinct currency codes
- **Historical records**: Complete timeline of currency transitions
- **Update frequency**: Daily synchronization with source data
- **Data quality**: Validated against multiple authoritative sources

## 🤝 Contributing

### Reporting Issues
- **Data Inaccuracies**: Report via GitHub Issues with specific country/currency details
- **Missing Coverage**: Suggest additional territories or currencies
- **Format Requests**: Propose new output formats or data structures

### Development Contributions
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/enhancement`)
3. **Test** your changes thoroughly
4. **Commit** with descriptive messages
5. **Submit** pull request with detailed description

### Data Source Issues
If you identify issues with source data:
1. Verify against multiple sources (Unicode CLDR, ISO standards)
2. Document the discrepancy with evidence
3. Propose correction with authoritative references

### Enhancement Ideas
- Additional data formats (XML, YAML, etc.)
- Regional currency groupings
- Exchange rate integration
- Historical exchange rate data
- API endpoint development

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

The currency data itself is derived from public standards and authoritative sources:
- Unicode CLDR: Unicode License
- ISO 4217/3166: International standards
- pycountry: LGPL 2.1

## 🔗 Related Projects

- [Unicode CLDR](https://cldr.unicode.org/) - Source of currency-territory mappings
- [pycountry](https://github.com/flyingcircusio/pycountry) - ISO country/currency database
- [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) - Currency code standard

---

**Last Updated**: Automatically maintained  
**Data Version**: See metadata.json for current version  
**Generator Version**: 1.2.0