import json
import os
import sys
from datetime import datetime
from dnscrypt_parser import DNSCryptParser
from doh_parser import DOHParser
from normalizer import Normalizer
from deduplicator import Deduplicator
from classifier import Classifier
from generator import Generator

def main():
    try:
        os.makedirs('../data', exist_ok=True)
        
        dnscrypt_data = DNSCryptParser.fetch()
        doh_data = DOHParser.fetch()
        
        all_dns = dnscrypt_data + doh_data
        
        if not all_dns:
            print("No DNS data collected")
            sys.exit(1)
        
        normalized = Normalizer.normalize(all_dns)
        validated = Normalizer.validate(normalized)
        deduplicated = Deduplicator.deduplicate(validated)
        classified = Classifier.classify(deduplicated)
        
        generator = Generator(classified)
        generator.save()
        
        print("DNS collection completed successfully")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
