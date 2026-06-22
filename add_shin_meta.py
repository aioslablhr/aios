"""Add metadata from site to Shin raw folder."""
import os

out_dir = '/app/companies/shin-travels/raw'
os.makedirs(out_dir, exist_ok=True)

meta = """# Shin Travels — Company Overview

Based: East London, UK
Founded: 1998
Website: https://shintravels.co.uk
Accreditations: ATOL-protected, IATA-accredited

## Core Services
1. Flight Booking — International and domestic routes, multi-airline support
2. Umrah Packages — Complete Umrah travel arrangements
3. Hajj Packages — Full Hajj travel services
4. Bespoke Holidays — Custom-tailored travel itineraries
5. Visa Services — Support for travel documentation

## Destinations Served
- Pakistan (primary route — flights to Lahore, Karachi, Islamabad)
- India
- Bangladesh
- Dubai / UAE
- Middle East (for Umrah/Hajj — Saudi Arabia)
- Beyond (global destinations)

## Target Market
British Pakistani families in East London and UK-wide. Community-focused travel agency serving the British Pakistani diaspora since 1998.

## Key Differentiators
- Since 1998 — over 25 years of experience
- ATOL protected — financial protection for customers
- IATA accredited — recognized industry standard
- Community-focused — understands British Pakistani travel needs
- Halal-conscious travel arrangements
"""

with open(os.path.join(out_dir, 'company-overview.md'), 'w') as f:
    f.write(meta)
print(f"Added company-overview.md ({len(meta)} chars)")
