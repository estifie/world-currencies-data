#!/usr/bin/env python3
"""
Currency Data Synchronization Script

Fetches the latest currency data from Unicode CLDR and generates CSV files
with current and historical currency information for all countries.
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, date
import json
import os
import logging
from typing import Dict, List, Optional, Tuple
import pycountry

# Configuration
GENERATOR_VERSION = "1.2.0"
CLDR_DATA_URL = "https://raw.githubusercontent.com/unicode-org/cldr/main/common/supplemental/supplementalData.xml"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CurrencyDataProcessor:
    def __init__(self):
        self.iso3166_data = {}
        self.iso4217_data = {}
        self.currency_regions = {}
        
    def fetch_iso3166_data(self) -> Dict:
        """Fetch ISO 3166 country codes and names from pycountry"""
        try:
            countries = {}
            for country in pycountry.countries:
                countries[country.alpha_2] = {
                    'alpha_2': country.alpha_2,
                    'alpha_3': country.alpha_3,
                    'name': country.name,
                    'official_name': getattr(country, 'official_name', country.name)
                }
            
            logger.info(f"Fetched {len(countries)} ISO 3166 countries/territories")
            return countries
        except Exception as e:
            logger.error(f"Failed to fetch ISO 3166 data: {e}")
            return {}
    
    def fetch_iso4217_data(self) -> Dict:
        """Fetch ISO 4217 currency codes and names"""
        try:
            currencies = {}
            for currency in pycountry.currencies:
                currencies[currency.alpha_3] = {
                    'code': currency.alpha_3,
                    'name': currency.name,
                    'numeric': currency.numeric
                }
            
            logger.info(f"Fetched {len(currencies)} ISO 4217 currencies")
            return currencies
        except Exception as e:
            logger.error(f"Failed to fetch ISO 4217 data: {e}")
            return {}
    
    def fetch_cldr_currency_data(self) -> str:
        """Fetch the latest CLDR currency data XML"""
        
        try:
            response = requests.get(CLDR_DATA_URL, timeout=30)
            response.raise_for_status()
            logger.info("Successfully fetched CLDR currency data")
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch CLDR data: {e}")
            raise
    
    def parse_currency_xml(self, xml_content: str) -> Dict:
        """Parse the CLDR XML and extract currency information"""
        try:
            root = ET.fromstring(xml_content)
            currency_data = {}
            
            # Navigate to CLDR currency data structure
            currency_data_elem = root.find('.//currencyData')
            if currency_data_elem is None:
                raise ValueError("Could not find currencyData section in XML")
            
            for region_elem in currency_data_elem.findall('.//region'):
                region_code = region_elem.get('iso3166')
                if not region_code:
                    continue
                
                currencies = []
                for currency_elem in region_elem.findall('currency'):
                    currency_info = {
                        'iso4217': currency_elem.get('iso4217'),
                        'from': currency_elem.get('from'),
                        'to': currency_elem.get('to'),
                        'tender': currency_elem.get('tender', 'true')
                    }
                    currencies.append(currency_info)
                
                currency_data[region_code] = currencies
            
            logger.info(f"Parsed currency data for {len(currency_data)} regions")
            return currency_data
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}")
            raise
    
    def determine_current_currency(self, currencies: List[Dict]) -> Optional[Dict]:
        """Determine the current currency for a region"""
        current_date = date.today().strftime('%Y-%m-%d')
        
        for currency in currencies:
            # Exclude non-tender currencies (commemorative, etc.)
            if currency['tender'] == 'false':
                continue
                
            # Active currency: no end date specified
            if not currency['to']:
                return currency
            
            # Check if currency is still within valid date range
            to_date = currency['to']
            if to_date >= current_date:
                return currency
        
        return None
    
    def get_all_currencies(self, currencies: List[Dict]) -> List[Dict]:
        """Get ALL currencies for a region (both active and historical with complete timeline)"""
        all_currencies = []
        
        for currency in currencies:
            if currency['tender'] == 'false':
                continue
                
            all_currencies.append(currency)
        
        return sorted(all_currencies, key=lambda x: x['from'] or '0000-01-01')
    
    def is_valid_region(self, region_code: str, country_info: Dict) -> bool:
        """Check if region has valid ISO data and should be included"""
        country_name = country_info.get('name', 'Unknown')
        
        # Filter out regions without proper ISO 3166 recognition
        if country_name in ['Unknown', ''] or not country_name:
            return False
            
        if not country_info:
            return False
            
        return True

    def generate_current_currencies_csv(self, currency_data: Dict) -> pd.DataFrame:
        """Generate CSV data for current currencies"""
        rows = []
        
        for region_code, currencies in currency_data.items():
            country_info = self.iso3166_data.get(region_code, {})
            
            if not self.is_valid_region(region_code, country_info):
                continue
                
            current_currency = self.determine_current_currency(currencies)
            
            if current_currency:
                currency_info = self.iso4217_data.get(current_currency['iso4217'], {})
                
                row = {
                    'country_code': region_code,
                    'country_name': country_info.get('name'),
                    'official_country_name': country_info.get('official_name', country_info.get('name')),
                    'iso_alpha3_code': country_info.get('alpha_3', ''),
                    'currency_code': current_currency['iso4217'],
                    'currency_name': currency_info.get('name', current_currency['iso4217']),
                    'active_since': current_currency['from'] or 'Unknown',
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                rows.append(row)
        
        return pd.DataFrame(rows)
    
    def generate_historical_currencies_csv(self, currency_data: Dict) -> pd.DataFrame:
        """Generate CSV data for ALL currencies (complete historical timeline)"""
        rows = []
        current_date = date.today().strftime('%Y-%m-%d')
        
        for region_code, currencies in currency_data.items():
            country_info = self.iso3166_data.get(region_code, {})
            
            if not self.is_valid_region(region_code, country_info):
                continue
                
            all_currencies = self.get_all_currencies(currencies)
            
            for currency in all_currencies:
                currency_info = self.iso4217_data.get(currency['iso4217'], {})
                
                if not currency['to']:
                    status = 'Active'
                elif currency['to'] >= current_date:
                    status = 'Active'
                else:
                    status = 'Historical'
                
                row = {
                    'country_code': region_code,
                    'country_name': country_info.get('name'),
                    'official_country_name': country_info.get('official_name', country_info.get('name')),
                    'iso_alpha3_code': country_info.get('alpha_3', ''),
                    'currency_code': currency['iso4217'],
                    'currency_name': currency_info.get('name', currency['iso4217']),
                    'active_from': currency['from'] or 'Unknown',
                    'active_until': currency['to'] or '',
                    'status': status,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
                rows.append(row)
        
        df = pd.DataFrame(rows)
        # Sort: country alphabetically, active currencies first, then chronologically
        if not df.empty:
            df = df.sort_values(['country_code', 'status', 'active_from'], 
                              ascending=[True, False, True])
        return df
    
    def generate_current_currencies_json(self, currency_data: Dict) -> Dict:
        """Generate JSON data for current currencies"""
        data = {}
        
        for region_code, currencies in currency_data.items():
            country_info = self.iso3166_data.get(region_code, {})
            
            if not self.is_valid_region(region_code, country_info):
                continue
                
            current_currency = self.determine_current_currency(currencies)
            
            if current_currency:
                currency_info = self.iso4217_data.get(current_currency['iso4217'], {})
                
                data[region_code] = {
                    'country_name': country_info.get('name'),
                    'official_country_name': country_info.get('official_name', country_info.get('name')),
                    'iso_alpha3_code': country_info.get('alpha_3', ''),
                    'currency_code': current_currency['iso4217'],
                    'currency_name': currency_info.get('name', current_currency['iso4217']),
                    'active_since': current_currency['from'] or 'Unknown'
                }
        
        return data
    
    def generate_historical_currencies_json(self, currency_data: Dict) -> Dict:
        """Generate JSON data for ALL currencies (complete historical timeline)"""
        data = {}
        current_date = date.today().strftime('%Y-%m-%d')
        
        for region_code, currencies in currency_data.items():
            country_info = self.iso3166_data.get(region_code, {})
            
            if not self.is_valid_region(region_code, country_info):
                continue
                
            all_currencies = self.get_all_currencies(currencies)
            
            currency_list = []
            for currency in all_currencies:
                currency_info = self.iso4217_data.get(currency['iso4217'], {})
                
                if not currency['to']:
                    status = 'Active'
                elif currency['to'] >= current_date:
                    status = 'Active'
                else:
                    status = 'Historical'
                
                currency_list.append({
                    'currency_code': currency['iso4217'],
                    'currency_name': currency_info.get('name', currency['iso4217']),
                    'active_from': currency['from'] or 'Unknown',
                    'active_until': currency['to'] or '',
                    'status': status
                })
            
            if currency_list:
                data[region_code] = {
                    'country_name': country_info.get('name'),
                    'official_country_name': country_info.get('official_name', country_info.get('name')),
                    'iso_alpha3_code': country_info.get('alpha_3', ''),
                    'currencies': currency_list
                }
        
        return data
    
    def generate_iso_mappings(self) -> Dict:
        """Generate simplified ISO mapping formats"""
        return {
            'countries': {code: data['name'] for code, data in self.iso3166_data.items()},
            'currencies': {code: data['name'] for code, data in self.iso4217_data.items()},
            'alpha2_to_alpha3': {code: data['alpha_3'] for code, data in self.iso3166_data.items() if data.get('alpha_3')}
        }
    
    def save_metadata(self):
        """Save metadata about the update process"""
        metadata = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'total_regions': len(self.currency_regions),
            'generator_version': GENERATOR_VERSION
        }
        
        with open('data/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def run(self):
        """Main execution function"""
        logger.info("Starting currency data update process...")
        
        # Initialize output directory
        os.makedirs('data', exist_ok=True)
        
        # Load reference data from official sources
        logger.info("Fetching ISO 3166 data...")
        self.iso3166_data = self.fetch_iso3166_data()
        
        logger.info("Fetching ISO 4217 data...")
        self.iso4217_data = self.fetch_iso4217_data()
        
        # Fetch live currency-country mappings from Unicode CLDR
        logger.info("Fetching CLDR currency data...")
        xml_content = self.fetch_cldr_currency_data()
        
        logger.info("Parsing currency data...")
        self.currency_regions = self.parse_currency_xml(xml_content)
        
        # Generate output files in multiple formats
        logger.info("Generating current currencies CSV...")
        current_df = self.generate_current_currencies_csv(self.currency_regions)
        current_df.to_csv('data/current_currencies.csv', index=False)
        
        logger.info("Generating historical currencies CSV (all currencies with timeline)...")
        historical_df = self.generate_historical_currencies_csv(self.currency_regions)
        historical_df.to_csv('data/historical_currencies.csv', index=False)
        
        logger.info("Generating current currencies JSON...")
        current_json = self.generate_current_currencies_json(self.currency_regions)
        with open('data/current_currencies.json', 'w') as f:
            json.dump(current_json, f, indent=2, ensure_ascii=False)
        
        logger.info("Generating historical currencies JSON...")
        historical_json = self.generate_historical_currencies_json(self.currency_regions)
        with open('data/historical_currencies.json', 'w') as f:
            json.dump(historical_json, f, indent=2, ensure_ascii=False)
        
        logger.info("Generating ISO mappings...")
        iso_mappings = self.generate_iso_mappings()
        with open('data/iso_mappings.json', 'w') as f:
            json.dump(iso_mappings, f, indent=2, ensure_ascii=False)
        
        logger.info("Saving metadata...")
        self.save_metadata()
        
        logger.info(f"Process completed successfully!")
        logger.info(f"- Current currencies: {len(current_df)} regions")
        logger.info(f"- Historical currencies: {len(historical_df)} records")

def main():
    """Main entry point"""
    try:
        processor = CurrencyDataProcessor()
        processor.run()
        return 0
    except Exception as e:
        logger.error(f"Process failed: {e}")
        return 1

if __name__ == '__main__':
    exit(main())