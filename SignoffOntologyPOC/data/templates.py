"""
Signoff Ontology Mock Data Templates
Based on SRS 3.2.2 Application별 수행 시점 상세표
"""

DEFAULT_SIGNOFF_MATRIX = {
    "Pre-Layout": {
        "Voltage Finder": {"engine": "SPACE", "condition": ["SSPLVCT"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "Power at Gate": {"engine": "SPACE", "condition": ["SSPLVCT"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "PN Ratio": {"engine": "SPACE", "condition": ["SSPLVCT"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "FO Check": {"engine": "SPACE", "condition": ["SSPLVCT"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "Driver & Keeper": {"engine": "SPACE", "condition": ["SFLVCT", "FSLVCT"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "DC Path": {"engine": "SPACE", "condition": ["TTTVCT"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "Floating Node": {"engine": "SPACE", "condition": ["TTTVCT"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "PEC": {"engine": "SPACE", "condition": ["Normal"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
    },
    "Static": {
        "DSC": {"engine": "SPACE", "condition": ["SSPLVCT", "SSPLVHT"], "revisions": ["R20", "R30", "R40", "R50", "R60"]},
        "LSC": {"engine": "SPACE", "condition": ["SFLVCT", "FSLVCT"], "revisions": ["R10", "R20", "R30", "R40", "R50", "R60"]},
        "LS": {"engine": "SPACE", "condition": ["SFLVCT", "FSLVCT"], "revisions": ["R20", "R30", "R40", "R50", "R60"]},
        "Cana-TR (Static)": {"engine": "SPACE", "condition": ["FFPHVHT"], "revisions": ["R40", "R50", "R60"]},
    },
    "Post-Layout": {
        "CDA": {"engine": "SPACE/PrimeTime", "condition": ["SSPLVCT"], "revisions": ["R50", "R60"]},
        "STA": {"engine": "PrimeTime", "condition": ["SSPLVCT"], "revisions": ["R50", "R60"]},
    },
    "Dynamic": {
        "ADV Margin Analyzer": {"engine": "ADV", "condition": ["FSDB"], "revisions": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
        "Glitch Margin": {"engine": "SPACE/ADV", "condition": ["FSDB"], "revisions": ["R50", "R60"]},
        "Dynamic DC Path": {"engine": "SPACE/ADV", "condition": ["TRN", "FSDB"], "revisions": ["R50", "R60"]},
        "ADV Latch S/H": {"engine": "ADV", "condition": ["FSDB"], "revisions": ["R50", "R60"]},
    }
}

# HBM Configuration Template
HBM_CONFIG_TEMPLATE = {
    "product_id": "HBM4E",
    "product_type": "HBM",
    "active_revisions": ["R30"],
    "blocks": [
        {"block_name": "FULLCHIP", "block_type": "TOP", "instance_count": 50000000},
        {"block_name": "IO", "block_type": "FULLCHIP_NO_CORE", "instance_count": 2000000},
        {"block_name": "SRAM_A", "block_type": "MEMORY", "instance_count": 500000},
        {"block_name": "CORE", "block_type": "DIGITAL", "instance_count": 10000000},
    ],
    "signoff_matrix": {
        # Default will be populated from DEFAULT_SIGNOFF_MATRIX based on revision
    }
}
