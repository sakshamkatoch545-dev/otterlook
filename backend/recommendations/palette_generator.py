"""
Personalized Colour Palette Recommendation Engine.
Generates categorized color harmonies for Clothing, Makeup, Accessories,
Neutrals, and Colors to Avoid based on predicted undertone and skin metrics.
"""

import os
import json
import colorsys
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

    @staticmethod
    def _hex_to_rgb(hex_code: str) -> List[int]:
        hex_code = hex_code.lstrip("#")
        if len(hex_code) == 6:
            return [int(hex_code[i:i+2], 16) for i in (0, 2, 4)]
        return [200, 160, 130]

    @staticmethod
    def _hsv_to_hex(h: float, s: float, v: float) -> str:
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
        return f"#{int(round(r * 255)):02X}{int(round(g * 255)):02X}{int(round(b * 255)):02X}"

    def _generate_skin_harmonies(self, skin_metrics: Optional[Dict[str, Any]], undertone: str) -> List[Dict[str, Any]]:
        """
        Dynamically derives mathematical color wheel harmonies directly from the user's analyzed face skin color.
        """
        # Extract base skin RGB
        rep_hex = "#D4AF37"
        if skin_metrics and "representative_hex" in skin_metrics:
            rep_hex = skin_metrics["representative_hex"]
        
        rgb = self._hex_to_rgb(rep_hex)
        r_norm, g_norm, b_norm = [c / 255.0 for c in rgb]
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        base_h = h * 360.0

        # Adjust target value/lightness based on skin depth
        is_light_skin = v > 0.70
        is_deep_skin = v < 0.45

        val_accent = 0.55 if is_light_skin else (0.90 if is_deep_skin else 0.72)
        sat_accent = min(1.0, max(0.50, s * 1.5))

        harmonies = [
            {
                "name": "Skin Complementary Accent",
                "hex": self._hsv_to_hex((base_h + 180.0) % 360.0, sat_accent, val_accent),
                "rgb": self._hex_to_rgb(self._hsv_to_hex((base_h + 180.0) % 360.0, sat_accent, val_accent)),
                "harmony_type": "Complementary Contrast",
                "badge": "⚡ Optical Contrast",
                "description": f"Calculated exact optical 180° complement to your facial tone ({rep_hex}). Creates striking vibrancy without washing out skin."
            },
            {
                "name": "Analogous Golden Radiance",
                "hex": self._hsv_to_hex((base_h + 35.0) % 360.0, min(1.0, sat_accent * 0.9), min(1.0, val_accent * 1.15)),
                "rgb": self._hex_to_rgb(self._hsv_to_hex((base_h + 35.0) % 360.0, min(1.0, sat_accent * 0.9), min(1.0, val_accent * 1.15))),
                "harmony_type": "Analogous Glow",
                "badge": "✨ Dermal Glow",
                "description": "Neighboring warm-golden spectrum hue that amplifies the natural luminescence of your complexion."
            },
            {
                "name": "Analogous Coral/Rose Flush",
                "hex": self._hsv_to_hex((base_h - 30.0 + 360.0) % 360.0, min(1.0, sat_accent * 0.95), min(1.0, val_accent * 1.05)),
                "rgb": self._hex_to_rgb(self._hsv_to_hex((base_h - 30.0 + 360.0) % 360.0, min(1.0, sat_accent * 0.95), min(1.0, val_accent * 1.05))),
                "harmony_type": "Analogous Flush",
                "badge": "🌸 Rosy Flush",
                "description": "Harmonizes with cutaneous hemoglobin blush to provide a healthy, youthful aura."
            },
            {
                "name": "Triadic Gemstone Harmony",
                "hex": self._hsv_to_hex((base_h + 120.0) % 360.0, sat_accent * 0.85, val_accent),
                "rgb": self._hex_to_rgb(self._hsv_to_hex((base_h + 120.0) % 360.0, sat_accent * 0.85, val_accent)),
                "harmony_type": "Triadic Balance",
                "badge": "💎 Triadic Balance",
                "description": "A 120° equidistant vibrancy point creating high-fashion editorial balance with your facial skin."
            },
            {
                "name": "Triadic Royal Statement",
                "hex": self._hsv_to_hex((base_h + 240.0) % 360.0, min(1.0, sat_accent * 0.90), val_accent),
                "rgb": self._hex_to_rgb(self._hsv_to_hex((base_h + 240.0) % 360.0, min(1.0, sat_accent * 0.90), val_accent)),
                "harmony_type": "Triadic Statement",
                "badge": "👑 Royal Statement",
                "description": "A balanced 240° jewel point designed for statement blazers, evening gowns, and silk scarves."
            },
            {
                "name": "Monochromatic Tonal Depth",
                "hex": self._hsv_to_hex(base_h, min(1.0, s * 1.35), max(0.15, v * 0.48)),
                "rgb": self._hex_to_rgb(self._hsv_to_hex(base_h, min(1.0, s * 1.35), max(0.15, v * 0.48))),
                "harmony_type": "Tonal Dressing",
                "badge": "🧥 Tonal Chic",
                "description": "Matches the exact hue angle of your skin at a deep luxury value for effortlessly chic tonal dressing."
            }
        ]
        return harmonies

    def generate_recommendations(self, undertone: str, skin_metrics: Optional[Dict[str, Any]] = None, gender: Optional[str] = "all") -> Dict[str, Any]:
        """
        Generates structured palette and style recommendations tailored to the user's undertone and gender preference.
        
        Args:
            undertone: "Warm", "Cool", or "Neutral"
            skin_metrics: optional dict containing CIELAB L*, a*, b*, ITA
            gender: "female", "male", or "all"
            
        Returns:
            Dict containing core palette swatches, categorized recommendations, and avoid list.
        """
        undertone_key = undertone.capitalize()
        gender_mode = (gender or "all").lower().strip()
        
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

        # Makeup recommendations: only for female or all/unspecified
        makeup_recs = []
        if gender_mode in ("female", "all"):
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

        # 5. Seasonal Color Harmony Insight
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

        # 7. Dynamic Skin-Derived Harmonies (Directly computed from analyzed facial skin hex)
        skin_harmonies = self._generate_skin_harmonies(skin_metrics, undertone_key)

        # 8. Curated Matched World Colors (Filtered to user's skin undertone)
        world_spectrum = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "family": c.get("family", "all"),
                "category": c.get("category", "Clothing"),
                "undertones": c.get("undertones", []),
                "tags": c.get("tags", []),
                "description": c.get("description", "")
            }
            for c in matching_colors
        ]

        return {
            "undertone": undertone_key,
            "gender": gender_mode,
            "stylist_summary": stylist_summary,
            "foundation_advice": foundation_advice,
            "palette": core_palette,
            "skin_harmonies": skin_harmonies,
            "recommendations": {
                "clothing": clothing_recs,
                "makeup": makeup_recs,
                "accessories": accessory_recs,
                "neutrals": neutral_recs,
                "world_spectrum": world_spectrum
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
