"""
products.py — Multi-product registry.
Defines every product (HGEC, Banking, etc.) and their platform configs.
Adding a new product = add one entry to PRODUCTS dict.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Each product defines:
#   label       : Display name
#   short        : Short code used in SQLite table prefix
#   color        : Accent hex colour
#   icon_svg     : Inline SVG for the product switcher pill
#   description  : One-line subtitle in sidebar
#   platforms    : Dict of platform_key → platform config dict
#                  (same structure as PLATFORMS in platform_dashboard.py)
# ─────────────────────────────────────────────────────────────────────────────

# ── Shared BASE_DDL (same for all products) ───────────────────────────────────
BASE_DDL = """
CREATE TABLE IF NOT EXISTS {table} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT, article_id INTEGER, source TEXT,
    publication_date TEXT, headline TEXT, genre TEXT, program_status TEXT,
    beneficial_vol INTEGER DEFAULT 0, neutral_vol INTEGER DEFAULT 0,
    adverse_vol INTEGER DEFAULT 0, total_vol REAL DEFAULT 0,
    beneficial_art INTEGER DEFAULT 0, neutral_art INTEGER DEFAULT 0,
    adverse_art INTEGER DEFAULT 0, total_articles INTEGER DEFAULT 1,
    {extra}
    _platform TEXT
);
"""

PRODUCTS = {

    # ══════════════════════════════════════════════════════════════════════════
    # PRODUCT 1 — HGEC (Hindi General Entertainment Channels)
    # ══════════════════════════════════════════════════════════════════════════
    "hgec": {
        "label":       "HGEC",
        "full_label":  "Hindi GEC",
        "short":       "hgec",
        "color":       "#4F46E5",
        "description": "HGEC OVERVIEW",
        "icon_svg":    '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>',
        "platforms": {
            "print": {
                "label":"Print","icon":"🗞️","table":"hgec_print",
                "unit_opts":["Index","Reach (Total OTS)","CCMs (Coverage)","Articles"],
                "unit_keys":["index","readership","coverage","articles"],
                "col_map":{
                    "Company":"company","Article_Id":"article_id","Publication":"source",
                    "Edition":"edition","Publication_Date":"publication_date","AdRate":"ad_rate",
                    "Headline":"headline","Article_Length":"article_length","Genre":"genre",
                    "State":"state","Zone":"zone","Program_Status":"program_status",
                    "Beneficial_Coverage":"beneficial_vol","Neutral_Coverage":"neutral_vol",
                    "Adverse_Coverage":"adverse_vol","Total_Coverage":"total_vol",
                    "Beneficial_Articles":"beneficial_art","Neutral_Articles":"neutral_art",
                    "Adverse_Articles":"adverse_art","Total_Articles":"total_articles",
                    "Total_OTS_in_000s":"total_ots","Total_Readership_in_000s":"total_readership",
                    "coScore_Index":"coscore_index","Total_Index":"total_index",
                },
                "ddl_extra":"edition TEXT, ad_rate REAL, article_length INTEGER, state TEXT, zone TEXT, total_ots REAL DEFAULT 0, total_readership REAL DEFAULT 0, coscore_index REAL DEFAULT 0, total_index REAL DEFAULT 0,",
                "genre_col":"genre","segment_col":"zone","segment_label":"Zone",
                "vol_col":"total_vol","read_col":"total_readership","idx_col":"coscore_index",
            },
            "online": {
                "label":"Online","icon":"🌐","table":"hgec_online",
                "unit_opts":["Index","Reach (Total OTS)","CCMs (Coverage)","Articles"],
                "unit_keys":["index","readership","coverage","articles"],
                "col_map":{
                    "Company":"company","Article_Id":"article_id","Website":"source",
                    "Publication_Date":"publication_date","Headline":"headline","Genre":"genre",
                    "Program_Status":"program_status","Beneficial_Mentions":"beneficial_vol",
                    "Neutral_Mentions":"neutral_vol","Adverse_Mentions":"adverse_vol",
                    "Total_mentions":"total_vol","BN_mentions":"bn_vol",
                    "B_Articles":"beneficial_art","N_Articles":"neutral_art",
                    "A_Articles":"adverse_art","Total_Articles":"total_articles",
                    "BN_Articles":"bn_articles","coScore":"coscore_index","coScore_Articles":"coscore_art",
                },
                "ddl_extra":"bn_vol INTEGER DEFAULT 0, bn_articles INTEGER DEFAULT 0, coscore_index REAL DEFAULT 0, coscore_art REAL DEFAULT 0, total_readership REAL DEFAULT 0, total_index REAL DEFAULT 0,",
                "genre_col":"genre","segment_col":"source","segment_label":"Website",
                "vol_col":"total_vol","read_col":"total_vol","idx_col":"coscore_index",
            },
            "tv": {
                "label":"TV","icon":"📺","table":"hgec_tv",
                "unit_opts":["Seconds","Clips","Index"],
                "unit_keys":["coverage","articles","index"],
                "col_map":{
                    "Company":"company","Clip_Id":"article_id","Channel":"source",
                    "Program_Date":"publication_date","Program":"genre",
                    "Program_Telecast":"headline","Clip_Type":"program_status",
                    "Time_Band":"zone","Article_Length":"article_length",
                    "Total_seconds":"total_vol","Minutes":"total_readership",
                    "Personality":"edition","Program_Month":"state","Client":"segment",
                },
                "ddl_extra":"zone TEXT, article_length INTEGER DEFAULT 0, total_readership REAL DEFAULT 0, coscore_index REAL DEFAULT 0, total_index REAL DEFAULT 0, edition TEXT, state TEXT, segment TEXT,",
                "genre_col":"genre","segment_col":"source","segment_label":"Channel",
                "vol_col":"total_vol","read_col":"total_readership","idx_col":"total_readership",
            },
            "social": {
                "label":"Social Media","icon":"📱","table":"hgec_social",
                "unit_opts":["No. of Posts"],
                "unit_keys":["articles"],
                "col_map":{
                    "Company":"company","Post ID":"article_id","Platforms":"source",
                    "Post Date":"publication_date","Caption":"headline","Keyword":"genre",
                    "Vertical":"program_status","Type Of Content":"zone",
                    "Media Type":"edition","Profile Name":"state","Tonality":"segment",
                    "Like Count":"total_readership","View Count":"total_vol",
                    "Total Comment Count":"beneficial_art","Share Count":"neutral_art",
                    "Positive Sentiment":"beneficial_vol","Neutral Sentiment":"neutral_vol",
                    "Negative Sentiment":"adverse_vol","Hashtag Count":"article_length",
                },
                "ddl_extra":"zone TEXT, edition TEXT, state TEXT, segment TEXT, article_length INTEGER DEFAULT 0, total_readership REAL DEFAULT 0, coscore_index REAL DEFAULT 0, total_index REAL DEFAULT 0,",
                "genre_col":"genre","segment_col":"source","segment_label":"Platform",
                "vol_col":"total_vol","read_col":"total_readership","idx_col":"coscore_index",
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PRODUCT 2 — Banking (Axis Bank / Finance sector)
    # Extra columns: Month, Quarter, Sector, Circulation, EAV, Clips, Seconds
    # Online has Group_Name instead of Company
    # TV has Total_Seconds + Total_Clips instead of clips/minutes
    # ══════════════════════════════════════════════════════════════════════════
    "banking": {
        "label":       "Banking",
        "full_label":  "BANKING OVERVIEW",
        "short":       "bank",
        "color":       "#0891B2",
        "description": "Banking & Finance Sector",
        "icon_svg":    '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
        "platforms": {
            "print": {
                "label":"Print","icon":"🗞️","table":"bank_print",
                "unit_opts":["Index","Reach (Total OTS)","CCMs (Coverage)","Articles"],
                "unit_keys":["index","readership","coverage","articles"],
                "col_map":{
                    "Company":"company","Article_Id":"article_id","Publication":"source",
                    "Edition":"edition","Publication_Date":"publication_date","AdRate":"ad_rate",
                    "Headline":"headline","Article_Length":"article_length","Genre":"genre",
                    "State":"state","Zone":"zone",
                    "Month":"month","Quarter":"quarter","Sector":"sector",
                    "Circulation":"total_readership",
                    "Beneficial_Coverage":"beneficial_vol","Neutral_Coverage":"neutral_vol",
                    "Adverse_Coverage":"adverse_vol","Total_Coverage":"total_vol",
                    "Beneficial_Articles":"beneficial_art","Neutral_Articles":"neutral_art",
                    "Adverse_Articles":"adverse_art","Total_Articles":"total_articles",
                    "coScore_Index":"coscore_index","Total_Index":"total_index",
                    "Total_EAV_in_INR":"total_eav",
                    "Shared_Exclusive":"shared_exclusive",
                },
                "ddl_extra":"edition TEXT, ad_rate REAL, article_length INTEGER, state TEXT, zone TEXT, month TEXT, quarter TEXT, sector TEXT, total_readership REAL DEFAULT 0, coscore_index REAL DEFAULT 0, total_index REAL DEFAULT 0, total_eav REAL DEFAULT 0, shared_exclusive TEXT,",
                "genre_col":"genre","segment_col":"zone","segment_label":"Zone",
                "vol_col":"total_vol","read_col":"total_readership","idx_col":"coscore_index",
                "extra_kpi":"total_eav",
            },
            "online": {
                "label":"Online","icon":"🌐","table":"bank_online",
                "unit_opts":["Index","Reach (Total OTS)","CCMs (Coverage)","Articles"],
                "unit_keys":["index","readership","coverage","articles"],
                "col_map":{
                    # Online uses Group_Name not Company
                    "Group_Name":"company","Article_Id":"article_id","Publication":"source",
                    "Publication_Date":"publication_date","Headline":"headline","Genre":"genre",
                    "Month":"month","Sector":"sector",
                    "Beneficial_Coverage":"beneficial_vol","Neutral_Coverage":"neutral_vol",
                    "Adverse_Coverage":"adverse_vol","Total_Coverage":"total_vol",
                    "Beneficial_Articles":"beneficial_art","Neutral_Articles":"neutral_art",
                    "Adverse_Articles":"adverse_art","Total_Articles":"total_articles",
                    "coScore_Index":"coscore_index","Total_Index":"total_index",
                    "Circulation":"total_readership",
                    "Shared_Exclusive":"shared_exclusive",
                },
                "ddl_extra":"month TEXT, sector TEXT, total_readership REAL DEFAULT 0, coscore_index REAL DEFAULT 0, total_index REAL DEFAULT 0, shared_exclusive TEXT,",
                "genre_col":"genre","segment_col":"source","segment_label":"Publication",
                "vol_col":"total_vol","read_col":"total_readership","idx_col":"coscore_index",
            },
            "tv": {
                "label":"TV","icon":"📺","table":"bank_tv",
                "unit_opts":["Seconds","Clips","Index"],
                "unit_keys":["coverage","articles","index"],
                "col_map":{
                    "Company":"company","Clip_Id":"article_id","Channel":"source",
                    "Program_Date":"publication_date","Program":"genre",
                    "Program_Telecast":"headline","Genre":"program_status",
                    "Month":"month","Quarter":"quarter","Sector":"sector",
                    "Program_Slot":"zone","Shared_Exclusive":"shared_exclusive",
                    "Total_Seconds":"total_vol","Total_Clips":"total_articles",
                    "Beneficial_Clips":"beneficial_art","Neutral_Clips":"neutral_art",
                    "Adverse_Clips":"adverse_art",
                    "Beneficial_Seconds":"beneficial_vol","Neutral_Seconds":"neutral_vol",
                    "Adverse_Seconds":"adverse_vol",
                    "coScore_Index":"coscore_index","Reach":"total_readership",
                },
                "ddl_extra":"month TEXT, quarter TEXT, sector TEXT, zone TEXT, shared_exclusive TEXT, total_readership REAL DEFAULT 0, coscore_index REAL DEFAULT 0, total_index REAL DEFAULT 0,",
                "genre_col":"genre","segment_col":"source","segment_label":"Channel",
                "vol_col":"total_vol","read_col":"total_readership","idx_col":"coscore_index",
            },
        },
    },

}

def get_product(product_key: str) -> dict:
    return PRODUCTS.get(product_key, PRODUCTS["hgec"])

def get_platform(product_key: str, platform_key: str) -> dict:
    return PRODUCTS[product_key]["platforms"].get(platform_key, {})

def all_platform_keys(product_key: str) -> list:
    return list(PRODUCTS[product_key]["platforms"].keys())