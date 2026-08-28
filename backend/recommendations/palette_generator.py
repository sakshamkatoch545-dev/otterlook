"""
Personalized Colour Palette Recommendation Engine.
Generates categorized color harmonies for Clothing, Makeup, Accessories,
Neutrals, and Colors to Avoid based on predicted undertone and skin metrics.
"""

import os
import json
from typing import Dict, Any, List, Optional

class PaletteGenerator:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "colour_database.json")
            
        self.db_path = db_path
        self.colours = []
        self.avoid_rules = {}
        self._load_database()

    def _load_database(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.colours = data.get("colours", [])
                    self.avoid_rules = data.get("avoid_rules", {})
            except Exception as e:
                print(f"[PaletteGenerator] Error loading database: {e}")
        else:
            print(f"[PaletteGenerator] Database file not found at {self.db_path}")

    def generate_recommendations(self, undertone: str, skin_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates structured palette and style recommendations tailored to the user's undertone.
        
        Args:
            undertone: "Warm", "Cool", or "Neutral"
            skin_metrics: optional dict containing CIELAB L*, a*, b*, ITA
            
        Returns:
            Dict containing core palette swatches, categorized recommendations, and avoid list.
        """
        undertone_key = undertone.capitalize()
        
        # 1. Filter matching colors
        matching_colors = [
            c for c in self.colours
            if undertone_key in c.get("undertones", [])
        ]
        
        # 2. Extract Core Palette Swatches (Clothing & Core tags)
        core_palette = []
        for c in matching_colors:
            if c.get("category") == "Clothing" or "core" in c.get("tags", []):
                core_palette.append({
                    "name": c["name"],
                    "hex": c["hex"],
                    "rgb": c["rgb"],
                    "description": c.get("description", "")
                })
        # Keep top 8-10 swatches
        core_palette = core_palette[:10]

        # 3. Categorized Lists
        clothing_recs = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "description": c.get("description", ""),
                "tags": c.get("tags", [])
            }
            for c in matching_colors if c.get("category") == "Clothing"
        ]

        makeup_recs = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "sub_category": c.get("sub_category", "General"),
                "description": c.get("description", "")
            }
            for c in matching_colors if c.get("category") == "Makeup"
        ]

        accessory_recs = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "sub_category": c.get("sub_category", "Metals & Gems"),
                "description": c.get("description", "")
            }
            for c in matching_colors if c.get("category") == "Accessories"
        ]

        neutral_recs = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "description": c.get("description", "")
            }
            for c in matching_colors if c.get("category") == "Neutrals"
        ]

        # 4. Colors to Avoid
        avoid_list = self.avoid_rules.get(undertone_key, [])

        # 5. Seasonal Color Harmony Insight (Optional Advanced Feature)
        seasonal_info = self._calculate_seasonal_harmony(undertone_key, skin_metrics)

        # 6. Stylist Guidance Summary
        if undertone_key == "Warm":
            stylist_summary = (
                "Opt for rich, golden, and earthy tones such as terracotta, olive, mustard, and camel. "
                "Warm metals like yellow gold and brass beautifully amplify your natural complexion."
            )
            foundation_advice = "Look for foundation shades with yellow, golden, or peachy descriptors (e.g., 'Warm Beige', 'Honey', 'Golden Caramel')."
        elif undertone_key == "Cool":
            stylist_summary = (
                "Gravitate towards crisp, jewel, and berry tones including royal blue, lavender, deep plum, and emerald. "
                "Cool metals like sterling silver and platinum deliver a bright, radiant harmony."
            )
            foundation_advice = "Choose foundations labeled with pink, rosy, or neutral-cool descriptors (e.g., 'Porcelain Rose', 'Cool Sand', 'Espresso Cool')."
        else: # Neutral
            stylist_summary = (
                "You have remarkable versatility to wear both warm and cool shades. Soft jade, classic teal, dusty rose, and taupe "
                "serve as your most flattering anchors. Rose gold and mixed metals look exceptional."
            )
            foundation_advice = "Select balanced neutral shades (e.g., 'Buff', 'Neutral Sand', 'Classic Tan') that avoid strong yellow or pink cast."

        return {
            "undertone": undertone_key,
            "stylist_summary": stylist_summary,
            "foundation_advice": foundation_advice,
            "palette": core_palette,
            "recommendations": {
                "clothing": clothing_recs,
                "makeup": makeup_recs,
                "accessories": accessory_recs,
                "neutrals": neutral_recs
            },
            "less_recommended": avoid_list,
            "seasonal_harmony": seasonal_info
        }

    def _calculate_seasonal_harmony(self, undertone: str, skin_metrics: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Determines the 4-Season Color Sub-type (Spring/Autumn for Warm; Summer/Winter for Cool; Soft/True for Neutral).
        """
        lightness_l = 60.0
        if skin_metrics and "cielab" in skin_metrics:
            lightness_l = skin_metrics["cielab"].get("L", 60.0)

        if undertone == "Warm":
            if lightness_l >= 62.0:
                season = "Warm Spring"
                desc = "Light, clear, and vibrant golden tones with high luminescence."
                key_tones = ["Coral", "Peach", "Warm Turquoise", "Buttercup Gold"]
            else:
                season = "Warm Autumn"
                desc = "Deep, rich, and earthy spices with warm amber resonance."
                key_tones = ["Terracotta", "Olive Green", "Burnt Orange", "Spiced Rust"]
        elif undertone == "Cool":
            if lightness_l >= 62.0:
                season = "Cool Summer"
                desc = "Soft, muted, and delicate pastel tones with powdery blue undertones."
                key_tones = ["Soft Lavender", "Dusty Rose", "Sky Blue", "Periwinkle"]
            else:
                season = "Cool Winter"
                desc = "Vivid, high-contrast, jewel-saturated and icy tones."
                key_tones = ["Royal Sapphire", "Deep Plum", "Emerald Green", "Crisp Optic White"]
        else:
            season = "Soft / True Neutral"
            desc = "Balanced intermediate contrast with sophisticated muted harmonies."
            key_tones = ["Teal", "Dusty Rose", "Soft Sage", "Warm Taupe"]

        return {
            "season_name": season,
            "description": desc,
            "key_tones": key_tones
        }
