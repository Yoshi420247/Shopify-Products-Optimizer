#!/usr/bin/env python3
"""
Shopify Product Tag Generator for What You Need Products
Based on the tagging specification document.
Version 2 - More precise extraction focused on Title and Type
"""

import csv
import re
import html
from typing import List, Dict, Optional, Set

# ============================================================================
# CONFIGURATION - Tag Dimension Values
# ============================================================================

KNOWN_BRANDS = {
    'raw ': 'brand:raw',
    ' raw ': 'brand:raw',
    'zig zag': 'brand:zig-zag',
    'zig-zag': 'brand:zig-zag',
    'zigzag': 'brand:zig-zag',
    'vibes ': 'brand:vibes',
    ' vibes': 'brand:vibes',
    'elements ': 'brand:elements',
    ' elements': 'brand:elements',
    'cookies ': 'brand:cookies',
    ' cookies': 'brand:cookies',
    'lookah': 'brand:lookah',
    'puffco': 'brand:puffco',
    'maven ': 'brand:maven',
    ' maven ': 'brand:maven',
    'g-pen': 'brand:g-pen',
    'g pen': 'brand:g-pen',
    'gpen': 'brand:g-pen',
    'only quartz': 'brand:only-quartz',
    'eo vape': 'brand:eo-vape',
    'eo-vape': 'brand:eo-vape',
    'monark': 'brand:monark',
    '710 sci': 'brand:710-sci',
    '710-sci': 'brand:710-sci',
    '710sci': 'brand:710-sci',
    'peaselburg': 'brand:peaselburg',
    'scorch ': 'brand:scorch',
    ' scorch': 'brand:scorch',
    'empire glassworks': 'brand:empire-glassworks',
    'mj arsenal': 'brand:mj-arsenal',
    'ooze ': 'brand:ooze',
    ' ooze': 'brand:ooze',
    'pulsar': 'brand:pulsar',
    'higher standards': 'brand:higher-standards',
    'grav ': 'brand:grav',
    ' grav ': 'brand:grav',
    'famous x': 'brand:famous-x',
    'famous-x': 'brand:famous-x',
    'juicy jay': 'brand:juicy-jay',
    'juicy jays': 'brand:juicy-jay',
    'high hemp': 'brand:high-hemp',
    'king palm': 'brand:king-palm',
    'clipper': 'brand:clipper',
    ' bic ': 'brand:bic',
    'blazer ': 'brand:blazer',
    ' blazer': 'brand:blazer',
    'special blue': 'brand:special-blue',
    'newport ': 'brand:newport',
    'zico': 'brand:zico',
    'santa cruz shredder': 'brand:santa-cruz-shredder',
    'space case': 'brand:space-case',
    'sharpstone': 'brand:sharpstone',
    'cali crusher': 'brand:cali-crusher',
    'kannastor': 'brand:kannastor',
    'otto ': 'brand:otto',
    ' otto': 'brand:otto',
    'shine ': 'brand:shine',
    'blazy susan': 'brand:blazy-susan',
    ' ocb ': 'brand:ocb',
    'ocb ': 'brand:ocb',
    ' job ': 'brand:job',
    "randy's": 'brand:randy',
    'randys': 'brand:randy',
    'dab nation': 'brand:dab-nation',
}

# Type to family/pillar mapping
TYPE_MAPPING = {
    'bongs & water pipes': {
        'pillar': 'pillar:smokeshop-device',
        'family': 'family:glass-bong',
        'format': 'format:bong',
        'use': ['use:flower-smoking'],
        'default_material': ['material:glass'],
    },
    'dab rigs / oil rigs': {
        'pillar': 'pillar:smokeshop-device',
        'family': 'family:glass-rig',
        'format': 'format:rig',
        'use': ['use:dabbing'],
        'default_material': ['material:glass'],
    },
    'bubblers': {
        'pillar': 'pillar:smokeshop-device',
        'family': 'family:bubbler',
        'format': 'format:bubbler',
        'use': ['use:flower-smoking'],
        'default_material': ['material:glass'],
    },
    'hand pipes': {
        'pillar': 'pillar:smokeshop-device',
        'family': 'family:spoon-pipe',
        'format': 'format:pipe',
        'use': ['use:flower-smoking'],
        'default_material': ['material:glass'],
    },
    'one hitters & chillums': {
        'pillar': 'pillar:smokeshop-device',
        'family': 'family:chillum-onehitter',
        'format': 'format:pipe',
        'use': ['use:flower-smoking'],
        'default_material': ['material:glass'],
    },
    'nectar collectors & straws': {
        'pillar': 'pillar:smokeshop-device',
        'family': 'family:nectar-collector',
        'format': 'format:nectar-collector',
        'use': ['use:dabbing'],
        'default_material': ['material:glass'],
    },
    'flower bowls': {
        'pillar': 'pillar:accessory',
        'family': 'family:flower-bowl',
        'format': 'format:accessory',
        'use': ['use:flower-smoking'],
        'default_material': ['material:glass'],
    },
    'carb caps': {
        'pillar': 'pillar:accessory',
        'family': 'family:carb-cap',
        'format': 'format:cap',
        'use': ['use:dabbing'],
        'default_material': ['material:glass'],
    },
    'dab tools / dabbers': {
        'pillar': 'pillar:accessory',
        'family': 'family:dab-tool',
        'format': 'format:tool',
        'use': ['use:dabbing'],
        'default_material': ['material:metal'],
    },
    'grinders': {
        'pillar': 'pillar:accessory',
        'family': 'family:grinder',
        'format': 'format:grinder',
        'use': ['use:flower-smoking'],  # Per spec line 498
        'default_material': ['material:metal'],
    },
    'rolling papers': {
        'pillar': 'pillar:accessory',
        'family': 'family:rolling-paper',
        'format': 'format:paper',
        'use': ['use:rolling'],
        'default_material': [],
    },
    'torches': {
        'pillar': 'pillar:accessory',
        'family': 'family:torch',
        'format': 'format:torch',
        'use': ['use:dabbing'],
        'default_material': ['material:metal'],
    },
    'electronics': {
        'pillar': 'pillar:accessory',
        'family': 'family:vape-battery',
        'format': 'format:battery-mod',
        'use': ['use:dabbing'],
        'default_material': ['material:metal'],
    },
    'essentials & accessories': {
        'pillar': 'pillar:accessory',
        'family': None,  # Needs to be determined from content
        'format': 'format:accessory',
        'use': ['use:flower-smoking'],
        'default_material': ['material:glass'],
    },
    # Theme types - need to determine family from content
    'quartz': {
        'pillar': 'pillar:accessory',
        'family': 'family:banger',
        'format': 'format:banger',
        'use': ['use:dabbing'],
        'default_material': ['material:quartz'],
    },
    'silicone': {
        'pillar': None,  # Determine from content
        'family': None,  # Determine from content
        'format': None,
        'use': None,
        'default_material': ['material:silicone'],
    },
    'pendants': {
        # Most pendants are decorative - determine from content if carb cap
        'pillar': None,  # Determine from content
        'family': None,  # Determine from content
        'format': None,
        'use': None,
        'default_material': ['material:glass'],
    },
    'packaging': {
        'pillar': 'pillar:packaging',
        'family': 'family:storage-accessory',
        'format': 'format:box',
        'use': ['use:storage'],
        'default_material': [],
    },
    'made in usa': {
        'pillar': None,  # Determine from content
        'family': None,  # Determine from content
        'format': None,
        'use': None,
        'style_override': ['style:made-in-usa'],
        'default_material': ['material:glass'],
    },
    'wyn brands': {
        'pillar': None,  # Determine from content
        'family': None,  # Determine from content
        'format': None,
        'use': None,
        'style_override': ['style:brand-highlight'],
        'default_material': ['material:glass'],
    },
}


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_brand(title: str) -> Optional[str]:
    """Extract brand from title only (more precise)."""
    title_lower = f" {title.lower()} "

    # Check for known brands (longer names first to avoid partial matches)
    sorted_brands = sorted(KNOWN_BRANDS.keys(), key=len, reverse=True)
    for brand_name in sorted_brands:
        if brand_name in title_lower:
            return KNOWN_BRANDS[brand_name]

    return None


def extract_materials_from_spec(title: str, body: str) -> List[str]:
    """Extract material tags from product specification sections only."""
    materials = set()

    # First check title for explicit materials
    title_lower = title.lower()

    # Check title for materials
    if 'borosilicate' in title_lower:
        materials.add('material:glass')
        materials.add('material:borosilicate')
    elif 'glass' in title_lower:
        materials.add('material:glass')

    if 'quartz' in title_lower:
        materials.add('material:quartz')

    if 'silicone' in title_lower:
        materials.add('material:silicone')

    if 'titanium' in title_lower:
        materials.add('material:titanium')

    if 'stainless' in title_lower:
        materials.add('material:stainless-steel')

    if 'ceramic' in title_lower:
        materials.add('material:ceramic')

    if 'wood' in title_lower or 'wooden' in title_lower:
        materials.add('material:wood')

    if 'metal' in title_lower or 'aluminum' in title_lower:
        materials.add('material:metal')

    # Check body for materials in specification sections
    body_lower = body.lower() if body else ""

    # Look for material in spec table or explicit material mentions
    if 'borosilicate' in body_lower:
        materials.add('material:glass')
        materials.add('material:borosilicate')

    # Look for explicit material specification
    mat_match = re.search(r'material[:\s]+(\w+)', body_lower)
    if mat_match:
        mat = mat_match.group(1)
        if 'borosilicate' in mat or 'boro' in mat:
            materials.add('material:glass')
            materials.add('material:borosilicate')
        elif 'glass' in mat:
            materials.add('material:glass')
        elif 'quartz' in mat:
            materials.add('material:quartz')
        elif 'silicone' in mat:
            materials.add('material:silicone')
        elif 'titanium' in mat:
            materials.add('material:titanium')
        elif 'ceramic' in mat:
            materials.add('material:ceramic')
        elif 'wood' in mat:
            materials.add('material:wood')
        elif 'metal' in mat or 'aluminum' in mat:
            materials.add('material:metal')

    return list(materials)


def extract_joint_details(title: str, body: str) -> List[str]:
    """Extract joint size, angle, and gender from title and body."""
    # Prioritize title
    combined = f"{title} {body}".lower()
    joint_tags = []

    # Joint size patterns
    size_found = False
    size_patterns = [
        (r'\b10\s*mm\b', 'joint_size:10mm'),
        (r'\b10mm\b', 'joint_size:10mm'),
        (r'\b14\s*mm\b', 'joint_size:14mm'),
        (r'\b14mm\b', 'joint_size:14mm'),
        (r'\b18\s*mm\b', 'joint_size:18mm'),
        (r'\b18mm\b', 'joint_size:18mm'),
        (r'\b19\s*mm\b', 'joint_size:18mm'),
    ]

    for pattern, tag in size_patterns:
        if re.search(pattern, combined):
            if not size_found:
                joint_tags.append(tag)
                size_found = True
            break

    # Check title patterns like "14 MALE" or "18 FEMALE"
    title_size = re.search(r'\b(10|14|18|19)\s*(male|female|m|f)\b', title.lower())
    if title_size and not size_found:
        size = title_size.group(1)
        if size == '19':
            size = '18'
        joint_tags.append(f'joint_size:{size}mm')

    # Joint angle patterns
    if re.search(r'\b45\s*(degree|°|deg)?\b', combined) or '45°' in combined:
        joint_tags.append('joint_angle:45')
    elif re.search(r'\b90\s*(degree|°|deg)?\b', combined) or '90°' in combined:
        joint_tags.append('joint_angle:90')

    # Joint gender patterns
    if re.search(r'\bfemale\b', combined):
        joint_tags.append('joint_gender:female')
    elif re.search(r'\bmale\b', combined):
        joint_tags.append('joint_gender:male')
    elif re.search(r'\b\d+\s*f\b', title.lower()):
        joint_tags.append('joint_gender:female')
    elif re.search(r'\b\d+\s*m\b', title.lower()):
        joint_tags.append('joint_gender:male')

    return joint_tags


def extract_length(title: str) -> Optional[str]:
    """Extract length in inches from title only."""
    title_lower = title.lower()

    # Patterns for length in title
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:inch|inches|in|")',
        r"(\d+(?:\.\d+)?)[″'']",
        r'^(\d+)\s*(?:inch|in|"|″)',
        r'(\d+)\s*(?:INCH|inch|In|IN)\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            length = match.group(1)
            try:
                length_num = float(length)
                if length_num == int(length_num):
                    return f"length:{int(length_num)}in"
                else:
                    return f"length:{length}in"
            except:
                return f"length:{length}in"

    return None


def extract_capacity(title: str) -> Optional[str]:
    """Extract capacity for jars/packaging from title."""
    title_lower = title.lower()

    # ML patterns
    ml_match = re.search(r'(\d+)\s*ml\b', title_lower)
    if ml_match:
        return f"capacity:{ml_match.group(1)}ml"

    # OZ patterns
    oz_match = re.search(r'(\d+)\s*oz\b', title_lower)
    if oz_match:
        return f"capacity:{oz_match.group(1)}oz"

    return None


def extract_bundle(title: str) -> Optional[str]:
    """Extract pack/bundle size from title."""
    title_lower = title.lower()

    # Pack patterns
    pack_patterns = [
        (r'(\d+)\s*(?:-\s*)?pack\b', lambda m: f"bundle:{m.group(1)}-pack"),
        (r'(\d+)\s*(?:pk|pc|pcs|pieces?|count|ct)\b', lambda m: f"bundle:{m.group(1)}-pack"),
        (r'\bdisplay\s*(?:box|case)?\b', lambda m: "bundle:display-box"),
        (r'\bcarton\b', lambda m: "bundle:display-box"),
        (r'\bbulk\s*(?:case|box)?\b', lambda m: "bundle:bulk-case"),
    ]

    for pattern, handler in pack_patterns:
        match = re.search(pattern, title_lower)
        if match:
            result = handler(match)
            # Handle high counts
            if 'bundle:' in result and '-pack' in result:
                try:
                    count = int(re.search(r'(\d+)', result).group(1))
                    if count > 50:
                        return "bundle:bulk-case"
                    elif count > 24:
                        return "bundle:display-box"
                except:
                    pass
            return result

    return None


def extract_styles(title: str, body: str, product_type: str) -> List[str]:
    """Extract style tags - be conservative."""
    styles = []
    title_lower = title.lower()
    product_type_lower = product_type.lower()

    # Check specification section for Made in USA
    body_lower = body.lower() if body else ""

    # Made in USA - check type and explicit spec mentions
    if 'made in usa' in product_type_lower:
        styles.append('style:made-in-usa')
    elif 'usa' in title_lower and 'made' in body_lower:
        # Check if body explicitly mentions made in USA
        if re.search(r'made\s+in\s+(?:the\s+)?usa', body_lower):
            styles.append('style:made-in-usa')
        elif 'american-made' in body_lower or 'american made' in body_lower:
            styles.append('style:made-in-usa')
        elif 'hand-crafted in' in body_lower and ('usa' in body_lower or ', wa' in body_lower or ', or' in body_lower or ', ca' in body_lower):
            styles.append('style:made-in-usa')

    # Also check for explicit origin mentions
    if re.search(r'(?:made|crafted|built)\s+in\s+(?:spokane|eugene|portland|los angeles|san diego|denver)', body_lower):
        if 'style:made-in-usa' not in styles:
            styles.append('style:made-in-usa')

    # Heady/art glass - from spec sections or title
    if 'heady' in title_lower:
        styles.append('style:heady')
    elif 'collab' in title_lower:
        styles.append('style:heady')
    elif 'heady glass' in body_lower or 'heady dab rig' in body_lower:
        # Check category section
        if re.search(r'category[:\s]+.*heady', body_lower):
            styles.append('style:heady')
        elif 'one-of-a-kind' in body_lower or 'one of a kind' in body_lower:
            styles.append('style:heady')
        elif 'collab' in body_lower and 'artist' in body_lower:
            styles.append('style:heady')

    # Animal themed - only if in title
    animal_terms = ['dragon', 'shark', 'owl', 'turtle', 'bird', 'frog', 'cat', 'dog', 'snake', 'octopus', 'fish', 'skull', 'monster', 'animal', 'dino', 'dinosaur']
    for term in animal_terms:
        if term in title_lower:
            styles.append('style:animal')
            break

    # Brand highlight (Wyn Brands type)
    if 'wyn brands' in product_type_lower:
        styles.append('style:brand-highlight')

    # Travel friendly - only if explicitly stated
    if 'travel' in title_lower or 'pocket' in title_lower or 'mini' in title_lower:
        styles.append('style:travel-friendly')

    return list(set(styles))


def determine_family_from_content(title: str, body: str, product_type: str) -> Dict:
    """Determine family and pillar from content for theme types."""
    title_lower = title.lower()
    body_lower = body.lower() if body else ""

    # Check title first for product type indicators

    # Rigs (check first because "rig" is specific)
    if 'rig' in title_lower or 'recycler' in title_lower:
        if 'silicone' in title_lower:
            return {
                'pillar': 'pillar:smokeshop-device',
                'family': 'family:silicone-rig',
                'format': 'format:rig',
                'use': ['use:dabbing'],
            }
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:glass-rig',
            'format': 'format:rig',
            'use': ['use:dabbing'],
        }

    # Bongs
    if 'bong' in title_lower or 'water pipe' in title_lower or 'waterpipe' in title_lower or 'beaker' in title_lower:
        if 'silicone' in title_lower:
            return {
                'pillar': 'pillar:smokeshop-device',
                'family': 'family:silicone-bong',
                'format': 'format:bong',
                'use': ['use:flower-smoking'],
            }
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:glass-bong',
            'format': 'format:bong',
            'use': ['use:flower-smoking'],
        }

    # Bubblers
    if 'bubbler' in title_lower:
        if 'joint' in title_lower or 'pre-roll' in title_lower or 'preroll' in title_lower:
            return {
                'pillar': 'pillar:smokeshop-device',
                'family': 'family:joint-bubbler',
                'format': 'format:bubbler',
                'use': ['use:flower-smoking', 'use:setup-protection'],
            }
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:bubbler',
            'format': 'format:bubbler',
            'use': ['use:flower-smoking'],
        }

    # Hand pipes
    if 'pipe' in title_lower or 'spoon' in title_lower or 'sherlock' in title_lower or 'steamroller' in title_lower or 'hammer' in title_lower:
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:spoon-pipe',
            'format': 'format:pipe',
            'use': ['use:flower-smoking'],
        }

    # Chillums/One hitters
    if 'chillum' in title_lower or 'one hitter' in title_lower or 'one-hitter' in title_lower or 'taster' in title_lower:
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:chillum-onehitter',
            'format': 'format:pipe',
            'use': ['use:flower-smoking'],
        }

    # Nectar collectors
    if 'nectar collector' in title_lower or 'honey straw' in title_lower or 'dab straw' in title_lower:
        if 'electronic' in title_lower or 'electric' in title_lower:
            return {
                'pillar': 'pillar:smokeshop-device',
                'family': 'family:electronic-nectar-collector',
                'format': 'format:nectar-collector',
                'use': ['use:dabbing'],
            }
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:nectar-collector',
            'format': 'format:nectar-collector',
            'use': ['use:dabbing'],
        }

    # Bangers
    if 'banger' in title_lower or 'slurper' in title_lower or 'terp slurper' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:banger',
            'format': 'format:banger',
            'use': ['use:dabbing'],
        }

    # Carb caps
    if 'carb cap' in title_lower or 'carbcap' in title_lower or ('cap' in title_lower and 'dab' in body_lower):
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:carb-cap',
            'format': 'format:cap',
            'use': ['use:dabbing'],
        }

    # Flower bowls
    if 'bowl' in title_lower or 'slide' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:flower-bowl',
            'format': 'format:accessory',
            'use': ['use:flower-smoking'],
        }

    # Dab tools
    if 'dab tool' in title_lower or 'dabber' in title_lower or 'tool' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:dab-tool',
            'format': 'format:tool',
            'use': ['use:dabbing'],
        }

    # Grinders
    if 'grinder' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:grinder',
            'format': 'format:grinder',
            'use': ['use:preparation'],
        }

    # Rolling papers
    if 'paper' in title_lower or 'cone' in title_lower or 'rolling' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:rolling-paper',
            'format': 'format:paper',
            'use': ['use:rolling'],
        }

    # Torches
    if 'torch' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:torch',
            'format': 'format:torch',
            'use': ['use:dabbing'],
        }

    # Ash catchers
    if 'ash catcher' in title_lower or 'ashcatcher' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:ash-catcher',
            'format': 'format:accessory',
            'use': ['use:setup-protection', 'use:flower-smoking'],
        }

    # Downstems
    if 'downstem' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:downstem',
            'format': 'format:accessory',
            'use': ['use:flower-smoking'],
        }

    # Trays
    if 'tray' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:tray',
            'format': 'format:tray',
            'use': ['use:rolling'],
        }

    # Storage/Jars
    if 'jar' in title_lower or 'stash' in title_lower or 'container' in title_lower or 'storage' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:storage-accessory',
            'format': 'format:jar',
            'use': ['use:storage'],
        }

    # Packaging/boxes
    if 'box' in title_lower:
        return {
            'pillar': 'pillar:packaging',
            'family': 'family:storage-accessory',
            'format': 'format:box',
            'use': ['use:storage'],
        }

    # Batteries/Vape
    if 'battery' in title_lower or 'vape pen' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:vape-battery',
            'format': 'format:battery-mod',
            'use': ['use:dabbing'],
        }

    # Coils
    if 'coil' in title_lower or 'atomizer' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:vape-coil',
            'format': 'format:coil',
            'use': ['use:dabbing'],
        }

    # Pendants - check for carb cap or pipe functionality
    if 'pendant' in title_lower:
        # Check if it's EXPLICITLY a carb cap pendant (must be in title or very early in description)
        # Title must contain "carb cap" OR first 300 chars of body must explicitly say it IS a carb cap
        is_carb_cap = False
        if 'carb cap' in title_lower:
            is_carb_cap = True
        elif body_lower:
            # Check if body explicitly says this IS a carb cap (not just comparing to one)
            first_part = body_lower[:300]
            if 'is a' in first_part and 'carb cap' in first_part:
                is_carb_cap = True
            elif 'carb cap that' in first_part or 'carb cap pendant' in first_part:
                is_carb_cap = True

        if is_carb_cap:
            return {
                'pillar': 'pillar:accessory',
                'family': 'family:carb-cap',
                'format': 'format:cap',
                'use': ['use:dabbing'],
            }
        # Check if it's a pipe pendant
        if 'pipe' in title_lower:
            return {
                'pillar': 'pillar:smokeshop-device',
                'family': 'family:spoon-pipe',
                'format': 'format:pipe',
                'use': ['use:flower-smoking'],
            }
        # Check body for pipe functionality in first 300 chars
        if body_lower and 'pipe' in body_lower[:300] and 'hand pipe' in body_lower[:400]:
            return {
                'pillar': 'pillar:smokeshop-device',
                'family': 'family:spoon-pipe',
                'format': 'format:pipe',
                'use': ['use:flower-smoking'],
            }
        # Otherwise it's decorative merch
        return {
            'pillar': 'pillar:merch',
            'family': 'family:merch-pendant',
            'format': 'format:pendant',
            'use': [],
        }

    # Matches - rolling accessory
    if 'match' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:rolling-accessory',
            'format': 'format:accessory',
            'use': ['use:rolling'],
        }

    # Drop downs - similar to downstems
    if 'drop down' in title_lower or 'dropdown' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:downstem',
            'format': 'format:accessory',
            'use': ['use:flower-smoking'],
        }

    # Ashtrays - rolling trays
    if 'ashtray' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:tray',
            'format': 'format:tray',
            'use': ['use:rolling'],
        }

    # Glass cleaners - rolling accessory (general accessory)
    if 'cleaner' in title_lower:
        return {
            'pillar': 'pillar:accessory',
            'family': 'family:rolling-accessory',
            'format': 'format:accessory',
            'use': ['use:flower-smoking'],
        }

    # Check body for hints if nothing found in title
    if 'dab rig' in body_lower or 'dabbing' in body_lower:
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:glass-rig',
            'format': 'format:rig',
            'use': ['use:dabbing'],
        }

    if 'hand pipe' in body_lower or 'flower pipe' in body_lower:
        return {
            'pillar': 'pillar:smokeshop-device',
            'family': 'family:spoon-pipe',
            'format': 'format:pipe',
            'use': ['use:flower-smoking'],
        }

    return None


def generate_tags_for_product(handle: str, title: str, body_html: str, product_type: str, vendor: str, existing_tags: str) -> List[str]:
    """Generate new tags for a single product."""

    # Only process What You Need products
    if vendor.strip().lower() != 'what you need':
        return None

    # Clean up inputs
    title = title.strip() if title else ""
    body = strip_html(body_html) if body_html else ""
    product_type = product_type.strip() if product_type else ""
    product_type_lower = product_type.lower()

    tags = []

    # Get type mapping
    type_info = TYPE_MAPPING.get(product_type_lower, None)

    # ALWAYS check content first for products that might be miscategorized
    # (e.g., ashtray listed under Rolling Papers, matches under Essentials)
    content_info = determine_family_from_content(title, body, product_type)

    # For theme types or unknown types, use content info
    if type_info is None or type_info.get('pillar') is None or type_info.get('family') is None:
        if content_info:
            if type_info:
                # Merge with existing type_info
                type_info = {**type_info, **content_info}
            else:
                type_info = content_info
    # For functional types, override if content clearly indicates different product
    elif content_info:
        # Check if title indicates a different product type than the Shopify Type
        title_lower = title.lower()
        override_keywords = ['ashtray', 'tray', 'match', 'cleaner', 'drop down', 'dropdown', 'pendant']
        for keyword in override_keywords:
            if keyword in title_lower:
                type_info = {**type_info, **content_info}
                break

    # If still no type_info, use default
    if not type_info or not type_info.get('pillar'):
        type_info = {
            'pillar': 'pillar:accessory',
            'family': 'family:storage-accessory',
            'format': 'format:accessory',
            'use': ['use:flower-smoking'],
            'default_material': ['material:glass'],
        }

    # 1. Add pillar
    if type_info.get('pillar'):
        tags.append(type_info['pillar'])

    # 2. Add family
    family = type_info.get('family')
    if family:
        tags.append(family)

    # 3. Add brand (from title only)
    brand = extract_brand(title)
    if brand:
        tags.append(brand)

    # 4. Add materials (from title and spec sections only)
    materials = extract_materials_from_spec(title, body)

    # If no materials found, use default from type
    if not materials and type_info.get('default_material'):
        materials = type_info['default_material']

    tags.extend(materials)

    # 5. Add format
    if type_info.get('format'):
        tags.append(type_info['format'])

    # 6. Add use tags
    if type_info.get('use'):
        tags.extend(type_info['use'])

    # 7. Add joint details
    joint_tags = extract_joint_details(title, body)
    tags.extend(joint_tags)

    # 8. Add length (from title)
    length = extract_length(title)
    if length:
        tags.append(length)

    # 9. Add capacity (from title)
    capacity = extract_capacity(title)
    if capacity:
        tags.append(capacity)

    # 10. Add styles (conservative)
    styles = extract_styles(title, body, product_type)

    # Apply style overrides from type
    if type_info.get('style_override'):
        for style in type_info['style_override']:
            if style not in styles:
                styles.append(style)

    tags.extend(styles)

    # 11. Add bundle (from title)
    bundle = extract_bundle(title)
    if bundle:
        tags.append(bundle)

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag and tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags


def process_csv(input_file: str, output_file: str):
    """Process the CSV file and generate new tags."""

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        rows = list(reader)

    # Track unique products (by handle) to avoid reprocessing image rows
    processed_handles = {}
    updated_rows = []
    products_processed = 0

    for row in rows:
        handle = row.get('Handle', '')
        title = row.get('Title', '')
        body_html = row.get('Body (HTML)', '')
        product_type = row.get('Type', '')
        vendor = row.get('Vendor', '')
        existing_tags = row.get('Tags', '')

        # If this is a main product row (has title), process it
        if title and handle:
            new_tags = generate_tags_for_product(
                handle, title, body_html, product_type, vendor, existing_tags
            )

            if new_tags is not None:
                # Store for this handle
                processed_handles[handle] = ', '.join(new_tags)
                row['Tags'] = processed_handles[handle]
                products_processed += 1

            updated_rows.append(row)

        # If this is an image/variant row (no title but has handle)
        elif handle and not title:
            # Keep the same tags as the main product (or blank for images)
            if handle in processed_handles:
                row['Tags'] = ''  # Image rows typically don't need tags
            updated_rows.append(row)

        else:
            # Keep row as-is
            updated_rows.append(row)

    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Processed {products_processed} products")
    print(f"Output written to: {output_file}")

    return products_processed


if __name__ == '__main__':
    input_csv = '/home/user/Shopify-Products-Optimizer/WYN PRODUCT EXPORT.csv'
    output_csv = '/home/user/Shopify-Products-Optimizer/WYN_PRODUCT_EXPORT_TAGGED.csv'

    process_csv(input_csv, output_csv)
