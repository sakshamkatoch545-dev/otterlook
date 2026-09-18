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
        Generates structured palette and style recommendations tailored dynamically to the user's
        exact skin metrics (L*, a*, b*, ITA, phototype, and contrast).
        """
        undertone_key = undertone.capitalize()
        gender_mode = (gender or "all").lower().strip()
        
        # 1. Filter matching colors
        matching_colors = [
            c for c in self.colours
            if undertone_key in c.get("undertones", [])
        ]
        
        # 2. Extract skin color metrics
        lightness_l = 60.0
        lab_a = 12.0
        lab_b = 16.0
        ita_angle = 20.0
        rep_hex = "#D4AF37"
        phototype = "Type III — Golden Medium"

        if skin_metrics:
            if "cielab" in skin_metrics and isinstance(skin_metrics["cielab"], dict):
                lightness_l = float(skin_metrics["cielab"].get("L", 60.0))
                lab_a = float(skin_metrics["cielab"].get("a", 12.0))
                lab_b = float(skin_metrics["cielab"].get("b", 16.0))
            elif "L" in skin_metrics:
                lightness_l = float(skin_metrics.get("L", 60.0))
                lab_a = float(skin_metrics.get("a", 12.0))
                lab_b = float(skin_metrics.get("b", 16.0))
            
            if "ita_angle" in skin_metrics:
                ita_angle = float(skin_metrics["ita_angle"])
            if "representative_hex" in skin_metrics:
                rep_hex = skin_metrics["representative_hex"]
            if "phototype_estimate" in skin_metrics:
                phototype = str(skin_metrics["phototype_estimate"])

        skin_rgb = self._hex_to_rgb(rep_hex)
        r_n, g_n, b_n = [c / 255.0 for c in skin_rgb]
        skin_h, skin_s, skin_v = colorsys.rgb_to_hsv(r_n, g_n, b_n)
        base_h = skin_h * 360.0

        is_light_skin = lightness_l >= 62.0
        is_deep_skin = lightness_l < 48.0
        is_olive = (lab_b > lab_a + 2.5)

        # 3. 12-Season Classification
        seasonal_info = self._calculate_seasonal_harmony(undertone_key, skin_metrics)
        season_tags = seasonal_info.get("tags", [])
        season_code = seasonal_info.get("season_code", "")

        black_color = {
            "name": "Obsidian Black",
            "hex": "#0A0A0A",
            "rgb": [10, 10, 10],
            "category": "Neutrals",
            "tags": ["core", "neutral", "contrast", "essential"],
            "description": "A high-contrast classic neutral providing crisp, striking definition that illuminates light and fair complexions."
        }

        avoid_black = {
            "name": "Pitch Black",
            "hex": "#000000",
            "rgb": [0, 0, 0],
            "reason": "Pitch black creates a harsh, low-contrast boundary on deeper skin tones, absorbing light and draining natural radiance. Opt instead for rich midnight navy, dark espresso, or deep charcoal."
        }

        # 4. Biometric Affinity Scoring Function
        def calculate_affinity(c: Dict[str, Any]) -> float:
            c_rgb = c.get("rgb", [120, 120, 120])
            c_lum = 0.299 * c_rgb[0] + 0.587 * c_rgb[1] + 0.114 * c_rgb[2]
            c_l = (c_lum / 255.0) * 100.0
            
            rn, gn, bn = [x / 255.0 for x in c_rgb]
            ch, cs, cv = colorsys.rgb_to_hsv(rn, gn, bn)
            c_h = ch * 360.0

            delta_h = min(abs(c_h - base_h), 360.0 - abs(c_h - base_h))
            delta_l = abs(c_l - lightness_l)

            score = 100.0

            # Contrast Flattery
            if is_light_skin:
                if delta_l >= 38.0:
                    score += 28.0
                elif delta_l <= 22.0 and cs < 0.45:
                    score += 16.0
                elif 20.0 <= delta_l < 38.0:
                    score += 18.0
            elif is_deep_skin:
                if c_l >= 45.0:
                    score += 30.0
                if cs >= 0.48:
                    score += 22.0
                if delta_l < 15.0 and cs < 0.35:
                    score -= 35.0
            else:
                if 22.0 <= delta_l <= 55.0:
                    score += 26.0
                else:
                    score += 12.0

            # Harmonic Hue Angle
            if 150.0 <= delta_h <= 210.0:
                score += 26.0
            elif 22.0 <= delta_h <= 52.0:
                score += 24.0
            elif (105.0 <= delta_h <= 135.0) or (225.0 <= delta_h <= 255.0):
                score += 18.0
            elif delta_h < 22.0:
                score += 14.0

            # Sub-Season & Tags
            c_tags = c.get("tags", [])
            if any(t in c_tags for t in season_tags):
                score += 26.0
            if "spring" in season_code and "spring" in c_tags:
                score += 22.0
            if "autumn" in season_code and "autumn" in c_tags:
                score += 22.0
            if "summer" in season_code and "summer" in c_tags:
                score += 22.0
            if "winter" in season_code and "winter" in c_tags:
                score += 22.0
            if is_deep_skin and "deep" in c_tags:
                score += 20.0
            if is_light_skin and ("light" in c_tags or "vibrant" in c_tags):
                score += 18.0

            # Carotenoid (b*) & Erythema (a*) Resonance
            if lab_b >= 18.0 and (c.get("family") in ("yellow", "orange", "brown") or "warm_earthy" in c_tags):
                score += 20.0
            if lab_a >= 13.0 and (c.get("family") in ("red", "pink", "purple") or "jewel" in c_tags):
                score += 18.0
            if is_olive and (c.get("family") == "green" or any(w in c.get("name", "").lower() for w in ("olive", "bronze", "teal"))):
                score += 24.0

            return score

        # Score matching colors
        scored_colors = [
            dict(c, affinity_score=calculate_affinity(c))
            for c in matching_colors
        ]
        scored_colors.sort(key=lambda x: x["affinity_score"], reverse=True)

        # 5. Synthesize 7-Swatch Signature Master Palette
        chosen_palette = []
        used_names = set()

        def pick_role(filter_fn):
            for c in scored_colors:
                if c["name"] not in used_names and filter_fn(c):
                    used_names.add(c["name"])
                    chosen_palette.append(c)
                    return
            for c in scored_colors:
                if c["name"] not in used_names:
                    used_names.add(c["name"])
                    chosen_palette.append(c)
                    return

        # Role 1: Power Contrast Anchor
        if is_light_skin:
            black_cand = next((c for c in scored_colors if "black" in c["name"].lower() or c["hex"] == "#0A0A0A"), black_color)
            used_names.add(black_cand["name"])
            chosen_palette.append(black_cand)
        elif is_deep_skin:
            pick_role(lambda c: (0.299*c.get("rgb",[120,120,120])[0] + 0.587*c.get("rgb",[120,120,120])[1] + 0.114*c.get("rgb",[120,120,120])[2])/2.55 >= 55 and "black" not in c["name"].lower())
        else:
            pick_role(lambda c: abs((0.299*c.get("rgb",[120,120,120])[0] + 0.587*c.get("rgb",[120,120,120])[1] + 0.114*c.get("rgb",[120,120,120])[2])/2.55 - lightness_l) >= 32)

        # Role 2: Dermal Radiance Enhancer (Analogous Glow)
        def is_analogous(c):
            rgb = c.get("rgb", [120, 120, 120])
            rn, gn, bn = [x / 255.0 for x in rgb]
            ch, _, _ = colorsys.rgb_to_hsv(rn, gn, bn)
            dh = min(abs(ch * 360.0 - base_h), 360.0 - abs(ch * 360.0 - base_h))
            return 18.0 <= dh <= 58.0 and c.get("category") == "Clothing"
        pick_role(is_analogous)

        # Role 3: Optical Complementary Statement
        def is_complement(c):
            rgb = c.get("rgb", [120, 120, 120])
            rn, gn, bn = [x / 255.0 for x in rgb]
            ch, _, _ = colorsys.rgb_to_hsv(rn, gn, bn)
            dh = min(abs(ch * 360.0 - base_h), 360.0 - abs(ch * 360.0 - base_h))
            return 140.0 <= dh <= 220.0
        pick_role(is_complement)

        # Role 4: Sartorial Tailoring Base
        pick_role(lambda c: (c.get("category") in ("Clothing", "Neutrals")) and any(w in (c.get("name", "") + " " + c.get("description", "")).lower() for w in ("camel", "navy", "olive", "espresso", "charcoal", "slate", "tailor", "suit", "coat")))

        # Role 5: Sub-Seasonal Signature Accent
        pick_role(lambda c: any(t in c.get("tags", []) for t in season_tags) and ("vibrant" in c.get("tags", []) or "accent" in c.get("tags", []) or c.get("category") == "Clothing"))

        # Role 6: Precious Metal & Fine Horology
        pick_role(lambda c: c.get("category") == "Accessories" or "metal" in c.get("tags", []) or any(m in c.get("name", "").lower() for m in ("gold", "silver", "bronze", "platinum", "titanium")))

        # Role 7: Evening Silk / Velvet Couture
        pick_role(lambda c: c.get("category") == "Clothing" and c["name"] not in used_names)

        while len(chosen_palette) < 7:
            pick_role(lambda c: True)

        core_palette = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "description": c.get("description", "")
            }
            for c in chosen_palette[:7]
        ]

        # 6. Categorized Recommendations
        clothing_recs = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "description": c.get("description", ""),
                "tags": c.get("tags", [])
            }
            for c in scored_colors if c.get("category") == "Clothing"
        ]
        if gender_mode == "male":
            clothing_recs = [
                c for c in clothing_recs
                if not any(w in c.get("description", "").lower() for w in ("dress", "skirt", "blouse"))
            ]

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
                for c in scored_colors if c.get("category") == "Makeup"
            ]

        accessory_recs = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "sub_category": c.get("sub_category", "Metals & Gems"),
                "description": c.get("description", "")
            }
            for c in scored_colors if c.get("category") == "Accessories"
        ]
        if gender_mode == "male":
            accessory_recs = [
                c for c in accessory_recs
                if any(w in (c.get("description", "") + " " + c.get("name", "")).lower() for w in ("watch", "cuff", "buckle", "leather", "metal", "gold", "silver", "bronze", "titanium"))
            ]

        neutral_recs = [
            {
                "name": c["name"],
                "hex": c["hex"],
                "rgb": c["rgb"],
                "description": c.get("description", "")
            }
            for c in scored_colors if c.get("category") == "Neutrals"
        ]

        # Avoid list
        avoid_list = list(self.avoid_rules.get(undertone_key, []))
        if is_light_skin:
            if not any("black" in c["name"].lower() for c in clothing_recs):
                clothing_recs = [black_color] + clothing_recs
            if not any("black" in c["name"].lower() for c in neutral_recs):
                neutral_recs = [black_color] + neutral_recs
            avoid_list = [a for a in avoid_list if "black" not in a.get("name", "").lower()]
            avoid_list.append({
                "name": "Muddy Mustard Yellow",
                "hex": "#8B7D12",
                "reason": "Dull, low-chroma muddy yellows impart a jaundiced, tired pallor to fair and light complexions. Opt for clear buttercup or champagne instead."
            })
        else:
            core_palette = [c for c in core_palette if "black" not in c["name"].lower() and c["hex"].upper() not in ("#0A0A0A", "#000000")]
            clothing_recs = [c for c in clothing_recs if "black" not in c["name"].lower() and c["hex"].upper() not in ("#0A0A0A", "#000000")]
            neutral_recs = [c for c in neutral_recs if "black" not in c["name"].lower() and c["hex"].upper() not in ("#0A0A0A", "#000000")]
            if not any("black" in a.get("name", "").lower() for a in avoid_list):
                avoid_list = [avoid_black] + avoid_list
            if is_deep_skin:
                avoid_list.append({
                    "name": "Chalky Pastel Grey",
                    "hex": "#C4C8D0",
                    "reason": "Chalky, desaturated pale greys create an unflattering ashy film against rich melanin. Choose crisp optic ivory or deep slate."
                })

        # Slices for clean presentation
        core_palette = core_palette[:7]
        clothing_recs = clothing_recs[:8]
        makeup_recs = makeup_recs[:6]
        accessory_recs = accessory_recs[:5]
        neutral_recs = neutral_recs[:4]
        avoid_list = avoid_list[:4]

        # 7. Stylist Guidance Summary
        season_desc = seasonal_info.get("description", "")
        if gender_mode == "male":
            gender_summary = (
                "Tailored specifically for masculine suiting: structured shoulders, obsidian black essentials, "
                "warm bronze/gold chronographs, and rich leather footwear."
                if undertone_key == "Warm"
                else "Calibrated for masculine presence: midnight navy suiting, icy blue shirting, and brushed platinum horology."
            )
        elif gender_mode == "female":
            gender_summary = (
                "Calibrated for feminine elegance: glowing silks, rich jewel accents, warm peach/coral blush, and fine jewelry."
                if undertone_key == "Warm"
                else "Calibrated for feminine grace: sapphire gowns, rose-petal blush, and glistening platinum jewelry."
            )
        else:
            gender_summary = f"Calibrated for {phototype} with L* {lightness_l:.1f} luminance."

        stylist_summary = f"{season_desc} {gender_summary}"

        if undertone_key == "Warm":
            foundation_advice = "Look for foundation shades with yellow, golden, or peachy descriptors (e.g., 'Warm Beige', 'Honey', 'Golden Caramel')."
        elif undertone_key == "Cool":
            foundation_advice = "Choose foundations labeled with pink, rosy, or neutral-cool descriptors (e.g., 'Porcelain Rose', 'Cool Sand', 'Espresso Cool')."
        else:
            foundation_advice = "Select balanced neutral shades (e.g., 'Buff', 'Neutral Sand', 'Classic Tan') that avoid strong yellow or pink cast."

        # 8. Dynamic Skin-Derived Harmonies
        skin_harmonies = self._generate_skin_harmonies(skin_metrics, undertone_key)

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
            for c in scored_colors
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
        Determines the 12-Season Color Sub-type based on CIELAB L*, a*, b*, and ITA.
        """
        lightness_l = 60.0
        lab_a = 12.0
        lab_b = 16.0
        ita_angle = 20.0
        skin_s = 0.35

        if skin_metrics:
            if "cielab" in skin_metrics and isinstance(skin_metrics["cielab"], dict):
                lightness_l = float(skin_metrics["cielab"].get("L", 60.0))
                lab_a = float(skin_metrics["cielab"].get("a", 12.0))
                lab_b = float(skin_metrics["cielab"].get("b", 16.0))
            elif "L" in skin_metrics:
                lightness_l = float(skin_metrics.get("L", 60.0))
                lab_a = float(skin_metrics.get("a", 12.0))
                lab_b = float(skin_metrics.get("b", 16.0))
            
            if "ita_angle" in skin_metrics:
                ita_angle = float(skin_metrics["ita_angle"])
            if "representative_hex" in skin_metrics:
                rgb = self._hex_to_rgb(skin_metrics["representative_hex"])
                _, skin_s, _ = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)

        is_light_skin = lightness_l >= 62.0
        is_deep_skin = lightness_l < 48.0
        is_olive = (lab_b > lab_a + 2.5)

        if undertone == "Warm":
            if lightness_l >= 68.0 or ita_angle >= 35.0:
                season = "Light Warm Spring"
                code = "light_spring"
                watermark = "SPRING"
                tags = ["spring", "light", "vibrant", "accent"]
                desc = "Delicate golden luminescence with fair porcelain radiance. Soft warm corals, champagne, and clear peach illuminate your delicate undertones."
                key_tones = ["Coral Pink", "Luminous Peach", "Buttercup Gold", "Warm Champagne"]
            elif (lightness_l >= 56.0 and skin_s >= 0.28) or (lab_b >= 20.0 and lightness_l >= 52.0):
                season = "Warm Bright Spring"
                code = "bright_spring"
                watermark = "SPRING"
                tags = ["spring", "vibrant", "accent", "core"]
                desc = "High-energy chromaticity with vibrant golden clarity. Fiery coral, bright marigold, poppy red, and warm turquoise create dazzling presence."
                key_tones = ["Vivid Coral", "Marigold", "Poppy Red", "Warm Amber"]
            elif is_deep_skin or ita_angle < 5.0:
                season = "Deep Warm Autumn"
                code = "deep_autumn"
                watermark = "AUTUMN"
                tags = ["autumn", "deep", "warm_earthy", "earthy"]
                desc = "Opulent melanin depth with concentrated warm resonance. Rich espresso, copper, spiced rust, and imperial olive command visual majesty."
                key_tones = ["Deep Bronze", "Spiced Rust", "Dark Espresso", "Burnt Copper"]
            else:
                season = "True Warm Autumn"
                code = "true_autumn"
                watermark = "AUTUMN"
                tags = ["autumn", "warm_earthy", "earthy", "core"]
                desc = "Classic golden-earth Mediterranean resonance. Baked terracotta, warm cognac, olive, and mustard gold bring out natural dermal glow."
                key_tones = ["Terracotta", "Olive Green", "Burnt Orange", "Mustard Gold"]

        elif undertone == "Cool":
            if lightness_l >= 68.0 or ita_angle >= 38.0:
                season = "Light Cool Summer"
                code = "light_summer"
                watermark = "SUMMER"
                tags = ["summer", "light", "soft", "accent"]
                desc = "Ethereal, delicate coolness with soft vascular radiance. Powdery sky blues, pastel lavender, and icy rose prevent visual heaviness."
                key_tones = ["Powder Blue", "Pastel Rose", "Soft Lavender", "Pearl Grey"]
            elif (lightness_l >= 54.0 and skin_s < 0.26) or (lab_b >= 6.0 and lightness_l >= 55.0 and lab_a < 12.0):
                season = "Soft Muted Summer"
                code = "muted_summer"
                watermark = "SUMMER"
                tags = ["summer", "soft", "muted", "core"]
                desc = "Velvety, understated cool sophistication. Low-contrast dusty rose, slate blue, and charcoal cashmere create a calm, refined silhouette."
                key_tones = ["Dusty Rose", "Slate Blue", "Heather Charcoal", "Smoky Mauve"]
            elif is_deep_skin or ita_angle < 5.0:
                season = "Deep Cool Winter"
                code = "deep_winter"
                watermark = "WINTER"
                tags = ["winter", "deep", "jewel", "core"]
                desc = "Dramatic nocturnal depth. Saturated royal sapphire, imperial amethyst, midnight navy, and ruby wine provide razor-sharp definition."
                key_tones = ["Midnight Navy", "Royal Sapphire", "Imperial Amethyst", "Ruby Wine"]
            elif (lightness_l >= 52.0 and lab_a >= 13.0) or (skin_s >= 0.32):
                season = "Bright Cool Winter"
                code = "bright_winter"
                watermark = "WINTER"
                tags = ["winter", "vibrant", "jewel", "contrast"]
                desc = "High-voltage icy clarity and jewel saturation. Pure optic white, icy cobalt, vivid fuchsia, and emerald jewel deliver breathtaking contrast."
                key_tones = ["Vivid Fuchsia", "Cobalt Blue", "Icy Violet", "Emerald Jewel"]
            else:
                season = "True Cool Summer"
                code = "true_summer"
                watermark = "SUMMER"
                tags = ["summer", "core", "blue", "jewel"]
                desc = "Pure subcutaneous hemoglobin balance. Classic French navy, raspberry silk, and crisp spruce teal enhance facial freshness."
                key_tones = ["French Navy", "Raspberry", "Spruce Teal", "Rose Quartz"]

        else: # Neutral
            if is_olive:
                season = "Luminous Olive Neutral"
                code = "olive_neutral"
                watermark = "OLIVE"
                tags = ["neutral", "earthy", "warm_earthy", "core"]
                desc = "Rare olive-matrix harmony balancing subtle green-golden undertones. Muted eucalyptus, bronze champagne, and toasted almond look flawless."
                key_tones = ["Muted Olive", "Bronze Champagne", "Soft Eucalyptus", "Toasted Almond"]
            elif lightness_l >= 60.0:
                season = "Soft Neutral Elegance"
                code = "soft_neutral"
                watermark = "NEUTRAL"
                tags = ["neutral", "soft", "light", "core"]
                desc = "Pristine harmonic equilibrium. Seamless versatility across dusty rose, soft jade, and blended neutral taupes without chromatic fatigue."
                key_tones = ["Dusty Teal", "Rose Gold", "Soft Sand", "Muted Jade"]
            else:
                season = "Deep Neutral Contrast"
                code = "deep_neutral"
                watermark = "NEUTRAL"
                tags = ["neutral", "deep", "core", "contrast"]
                desc = "Commanding multi-tonal neutrality with balanced melanin depth. Dark teal, espresso plum, and rich charcoal establish effortless authority."
                key_tones = ["Dark Teal", "Espresso Plum", "Rich Charcoal", "Smoky Copper"]

        return {
            "season_name": season,
            "season_code": code,
            "watermark": watermark,
            "description": desc,
            "key_tones": key_tones,
            "tags": tags
        }
