"""Test wiki loader inside Dograh container."""
import sys
sys.path.insert(0, "/app/api/services/workflow")
from wiki_loader import load_company_wiki

c = load_company_wiki("shin-travels")
print(f"Wiki loaded: {len(c)} chars")
print(c[:300])

c2 = load_company_wiki("imperium")
print(f"\nImperium wiki: {len(c2)} chars")
print(c2[:300])
