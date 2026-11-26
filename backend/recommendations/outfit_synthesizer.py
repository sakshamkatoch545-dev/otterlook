"""
Haute Couture Outfit Synthesis & Wardrobe Recommendation Engine.
Synthesizes 3 to 4 complete bespoke outfit looks (Upper, Bottom, Shoes, Jewellery/Makeup)
harmonized with the user's analyzed colour palette, undertone, preferred clothing type
(Casual, Formal, Streetwear, Ethnic, Party, Athleisure), gender, and weather conditions.
"""

from typing import Dict, Any, List, Optional
import random

CLOTHING_TYPES = [
    {"id": "all", "label": "All Kinds (Curated Mix)", "icon": "auto_awesome"},
    {"id": "casual", "label": "Casual & Everyday", "icon": "checkroom"},
    {"id": "formal", "label": "Formal & Business", "icon": "business_center"},
    {"id": "streetwear", "label": "Streetwear & Urban", "icon": "skateboarding"},
    {"id": "ethnic", "label": "Traditional & Ethnic", "icon": "temple_hindu"},
    {"id": "party", "label": "Party & Evening Glam", "icon": "local_bar"},
    {"id": "athleisure", "label": "Athleisure & Sporty", "icon": "fitness_center"},
]

WEATHER_TYPES = [
    {"id": "all", "label": "All Weathers", "icon": "public"},
    {"id": "summer", "label": "Summer & Hot", "icon": "wb_sunny"},
    {"id": "winter", "label": "Winter & Cold", "icon": "ac_unit"},
    {"id": "monsoon", "label": "Monsoon & Rainy", "icon": "rainy"},
    {"id": "spring_autumn", "label": "Spring / Autumn & Mild", "icon": "nature"},
]

# Wardrobe archetypes database mapping clothing type, weather, gender, and undertone harmonies
WARDROBE_DATABASE: Dict[str, Dict[str, Any]] = {
    "casual": {
        "summer": {
            "male": [
                {
                    "upper": {"name": "Camp-Collar Linen Shirt", "fabric": "100% Breathable European Linen", "silhouette": "Relaxed Camp Collar"},
                    "bottom": {"name": "Tailored Chino Shorts", "fabric": "Washed Lightweight Cotton Twill", "silhouette": "Mid-Thigh Tailored"},
                    "shoes": {"name": "Braided Leather Espadrilles", "material": "Full-Grain Leather & Natural Jute", "silhouette": "Low-Profile Slip-On"},
                    "jewellery": {
                        "rings": {"name": "Hammered Signet Ring", "metal": "18k Brushed Gold or Oxidized Silver"},
                        "earrings": {"name": "Minimalist Huggie Hoop", "metal": "Matte Finished Metal"},
                        "watch": {"name": "Minimalist Diver on Nato Strap", "dial": "Sunburst Dial with Canvas Strap"}
                    }
                },
                {
                    "upper": {"name": "Mercerized Cotton Resort Tee", "fabric": "Silky Mercerized Pima Cotton", "silhouette": "Clean Boxy Fit"},
                    "bottom": {"name": "Drawstring Linen-Blend Trousers", "fabric": "Linen & Cotton Weave", "silhouette": "Tapered Relaxed Leg"},
                    "shoes": {"name": "Minimalist Leather Court Sneakers", "material": "Supple Italian Napa Leather", "silhouette": "Low-Top Classic"},
                    "jewellery": {
                        "rings": {"name": "Slim Beveled Band", "metal": "Polished Metal Band"},
                        "earrings": {"name": "Geometric Square Stud", "metal": "Brushed Metal Stud"},
                        "watch": {"name": "Ultra-Thin Mesh Chrono", "dial": "Minimalist Bauhaus Dial"}
                    }
                },
                {
                    "upper": {"name": "Open-Weave Textured Polo", "fabric": "Organic Crochet Knit Cotton", "silhouette": "Retro Johnny Collar"},
                    "bottom": {"name": "Pleated Linen Bermuda Trousers", "fabric": "Crisp Belgian Linen", "silhouette": "Single Pleat Straight"},
                    "shoes": {"name": "Hand-Stitched Leather Slides", "material": "Vegetable-Tanned Calfskin", "silhouette": "Criss-Cross Slide"},
                    "jewellery": {
                        "rings": {"name": "Textured Coin Ring", "metal": "Satin Gold or Antique Silver"},
                        "earrings": {"name": "Micro Ball Ear Stud", "metal": "Surgical Titanium"},
                        "watch": {"name": "Vintage Field Watch", "dial": "Aged Patina Dial"}
                    }
                },
                {
                    "upper": {"name": "Short-Sleeve Slub Cotton Henley", "fabric": "Slub Weave Breathable Jersey", "silhouette": "Three-Button Casual"},
                    "bottom": {"name": "Light-Wash Selvedge Denim Shorts", "fabric": "Japanese 11oz Lightweight Denim", "silhouette": "Slim Tapered Cut"},
                    "shoes": {"name": "Woven Deck Shoes", "material": "Perforated Calf Leather", "silhouette": "Slip-on Deck"},
                    "jewellery": {
                        "rings": {"name": "Engraved Wave Signet", "metal": "Brushed Warm Alloy"},
                        "earrings": {"name": "Sleek Huggie Stud", "metal": "Low-Reflectance Metal"},
                        "watch": {"name": "Solar Chronograph", "dial": "Subtle Metallic Dial on Rubber"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Cropped Broderie Anglaise Blouse", "fabric": "Lightweight Cotton Voile", "silhouette": "Puff Sleeve Sweetheart"},
                    "bottom": {"name": "High-Rise Paperbag Linen Shorts", "fabric": "Washed Airy French Linen", "silhouette": "Paperbag Tie-Waist"},
                    "shoes": {"name": "Woven Strappy Sandalettes", "material": "Supple Nappa Leather Straps", "silhouette": "Ankle-Tie Flat Sandal"},
                    "jewellery": {
                        "necklace": {"name": "Dainty Freshwater Pearl Choker", "metal": "Fine Chain with Baroque Pearl"},
                        "earrings": {"name": "Twisted Ribbon Gold Hoops", "metal": "18k Warm Gold or Icy White Gold"},
                        "lipstick_tint": {"name": "Luminous Coral Glow Tint", "finish": "Dewy Stained Glass Finish", "shade_desc": "Fresh sun-kissed flush"}
                    }
                },
                {
                    "upper": {"name": "Ribbed Knit Halter Camisole", "fabric": "Silk & Modal Breathable Rib", "silhouette": "Sculpting Halter Neckline"},
                    "bottom": {"name": "Tiered Tier Gauze Maxi Skirt", "fabric": "Crinkle Cotton Muslin", "silhouette": "Flowing Tiered A-Line"},
                    "shoes": {"name": "Jute Platform Espadrille Wedges", "material": "Canvas Ribbon & Spanish Jute", "silhouette": "Wrap-Around Ankle Wedge"},
                    "jewellery": {
                        "necklace": {"name": "Layered Coin & Sunburst Pendant", "metal": "Multi-Strand Delicate Links"},
                        "earrings": {"name": "Hammered Disc Dangle Earrings", "metal": "Light-Catching Metallic Discs"},
                        "lipstick_tint": {"name": "Petal Peach Velvet Lip Stain", "finish": "Hydrating Velvet Stained Matte", "shade_desc": "Natural radiant flush"}
                    }
                },
                {
                    "upper": {"name": "Slouchy Linen Oversized Shirt", "fabric": "Pure Crushed European Linen", "silhouette": "Relaxed Boyfriend Slouch"},
                    "bottom": {"name": "Tailored High-Waist Linen Culottes", "fabric": "Structured Lightweight Linen", "silhouette": "Wide Leg Cropped"},
                    "shoes": {"name": "Sculptural Leather Mules", "material": "Buttery Glove Calfskin", "silhouette": "Square Toe Low Block"},
                    "jewellery": {
                        "necklace": {"name": "Organic Baroque Nugget Chain", "metal": "Heavy Chunky Textured Chain"},
                        "earrings": {"name": "Sculpted Abstract Wave Studs", "metal": "Molten Metal Organic Shape"},
                        "lipstick_tint": {"name": "Terracotta Sunset Dew Drops", "finish": "Glossy Sheer Oil Strobe", "shade_desc": "Warm amber luminous glaze"}
                    }
                },
                {
                    "upper": {"name": "Square-Neck Smocked Linen Top", "fabric": "Organic Elasticized Flax Linen", "silhouette": "Fitted Smocked Bodice"},
                    "bottom": {"name": "Button-Front Linen Midi Skirt", "fabric": "Mid-weight Linen Twill", "silhouette": "Flattering A-Line Slit"},
                    "shoes": {"name": "Criss-Cross Leather Slide Sandals", "material": "Hand-stitched Veg-Tan Leather", "silhouette": "Ergonomic Padded Slide"},
                    "jewellery": {
                        "necklace": {"name": "Herringbone Snake Chain", "metal": "Flexible Liquid Gold / Silver Chain"},
                        "earrings": {"name": "Chunky Teardrop Huggies", "metal": "Hollow Lightweight Drops"},
                        "lipstick_tint": {"name": "Rosewood Nude Velvet Gloss", "finish": "Cushion Satin Balm", "shade_desc": "My-lips-but-better sophisticated nude"}
                    }
                }
            ]
        },
        "winter": {
            "male": [
                {
                    "upper": {"name": "Chunky Cable-Knit Wool Sweater", "fabric": "100% Merino Wool & Cashmere", "silhouette": "Ribbed Crewneck Classic"},
                    "bottom": {"name": "Heavyweight Pleated Flannel Trousers", "fabric": "Brushed Wool Flannel", "silhouette": "Relaxed Taper with Cuffs"},
                    "shoes": {"name": "Handcrafted Leather Chelsea Boots", "material": "Waterproof Waxed Calfskin", "silhouette": "Elastic Gusset Ankle Boot"},
                    "jewellery": {
                        "rings": {"name": "Brushed Titanium Signet", "metal": "Satin Titanium Alloy"},
                        "earrings": {"name": "Obsidian Inset Stud", "metal": "Black Onyx with Metal Inlay"},
                        "watch": {"name": "Fluted Bezel Chronograph", "dial": "Deep Dial on Oiled Leather"}
                    }
                },
                {
                    "upper": {"name": "Merino Rollneck Under Overshirt", "fabric": "Ultra-Fine 120s Merino Wool", "silhouette": "Layered High Neck Turtleneck"},
                    "bottom": {"name": "Heavy Selvedge Indigo Denim", "fabric": "14oz Japanese Rigid Denim", "silhouette": "Classic Straight Leg"},
                    "shoes": {"name": "Commando-Sole Derby Brogues", "material": "Pebble-Grain Water-Resistant Leather", "silhouette": "Heavy Welted Derby"},
                    "jewellery": {
                        "rings": {"name": "Matte Faceted Band", "metal": "Satin Metal Band"},
                        "earrings": {"name": "Subtle Micro Huggie", "metal": "Brushed Metal Finish"},
                        "watch": {"name": "Pilot Automatic Horology", "dial": "High-Contrast Luminescent Numerals"}
                    }
                },
                {
                    "upper": {"name": "Waffle Knit Thermal with Shearling Overshirt", "fabric": "Heavy Cotton Thermal & Wool Blend", "silhouette": "Structured Overshirt Layer"},
                    "bottom": {"name": "Tailored Wool-Blend Chinos", "fabric": "Brushed Stretch Wool Twill", "silhouette": "Clean Modern Straight"},
                    "shoes": {"name": "Suede Combat Ankle Boots", "material": "Treated Weather-Resistant Suede", "silhouette": "Lace-Up Rugged Silhouette"},
                    "jewellery": {
                        "rings": {"name": "Hammered Dual-Band Ring", "metal": "Stacked Metal Rings"},
                        "earrings": {"name": "Minimal Carbon Fiber Stud", "metal": "Matte Black Inset"},
                        "watch": {"name": "Chronometer with Bronze Case", "dial": "Earthy Deep Textured Dial"}
                    }
                },
                {
                    "upper": {"name": "Brushed Cashmere Zip Cardigan", "fabric": "Pure Inner Mongolian Cashmere", "silhouette": "Stand Collar Zip Knit"},
                    "bottom": {"name": "Heavy Corduroy Relaxed Trousers", "fabric": "8-Wale Rich Cotton Corduroy", "silhouette": "Wide Relaxed Cut"},
                    "shoes": {"name": "Lug-Sole Moc-Toe Boots", "material": "Pull-Up Chromexcel Leather", "silhouette": "Reinforced Welt Lug Boot"},
                    "jewellery": {
                        "rings": {"name": "Signet with Tiger Eye Gem", "metal": "Warm Alloy with Semiprecious Stone"},
                        "earrings": {"name": "Sleek Brushed Ring Stud", "metal": "Low-Profile Titanium"},
                        "watch": {"name": "Heritage Field Watch on Suede", "dial": "Cream Matte Dial with Hand-Stitched Band"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Oversized Cashmere Turtleneck", "fabric": "Grade-A Mongolian Cashmere", "silhouette": "Generous Slouchy Fold Collar"},
                    "bottom": {"name": "Wide-Leg Wool Tailored Slacks", "fabric": "Italian Worsted Wool Twill", "silhouette": "Floor-Length Deep Pleat"},
                    "shoes": {"name": "Square-Toe Leather Ankle Boots", "material": "Buttery Smooth Box Calfskin", "silhouette": "Architectural Block Heel"},
                    "jewellery": {
                        "necklace": {"name": "Bold Chunky Anchor Chain", "metal": "High-Polish Warm / Cool Statement Links"},
                        "earrings": {"name": "Sculptural Molten Metal Drops", "metal": "Cast Heavy Drops"},
                        "lipstick_tint": {"name": "Velvet Spiced Berry / Rust", "finish": "Hydrating Velvet Matte", "shade_desc": "Intense rich winter depth"}
                    }
                },
                {
                    "upper": {"name": "Ribbed Wool Knit with Cocoon Cardigan", "fabric": "Merino & Alpaca Brushed Blend", "silhouette": "Draped Open-Front Cardigan"},
                    "bottom": {"name": "Tailored Suede Midi Skirt", "fabric": "Supple Micro-Suede Leather", "silhouette": "High-Waisted Center Slit"},
                    "shoes": {"name": "Knee-High Slouch Leather Boots", "material": "Burnished Italian Nappa", "silhouette": "Knee-High Sculpted Heel"},
                    "jewellery": {
                        "necklace": {"name": "Double Strand Snake Chain", "metal": "Liquid Metal High Luster"},
                        "earrings": {"name": "Oversized C-Curve Hoops", "metal": "Tubular Lightweight Metal"},
                        "lipstick_tint": {"name": "Bordeaux Wine Satin Strobe", "finish": "Cushioned Rich Stain", "shade_desc": "Dramatic vampy cool/warm wine"}
                    }
                },
                {
                    "upper": {"name": "Mock-Neck Knit Top with Wool Wrap", "fabric": "Fine Gauge Silk-Wool Jersey", "silhouette": "Second-Skin Fitted Knit"},
                    "bottom": {"name": "Heavy Crepe Flared Trousers", "fabric": "Triple-Crepe Wool Structured Weave", "silhouette": "Elongating Subtle Flare"},
                    "shoes": {"name": "Chunky Lug-Sole Chelsea Boots", "material": "Polished Spazzolato Leather", "silhouette": "Track Sole Pull-On"},
                    "jewellery": {
                        "necklace": {"name": "Coin Locket on Long Rope Chain", "metal": "Vintage Locket with Filigree"},
                        "earrings": {"name": "Stacked Mini Gem Hoops", "metal": "Emerald / Sapphire / Topaz Insets"},
                        "lipstick_tint": {"name": "Mulled Wine Cream Velvet", "finish": "Velvet Cushion Tint", "shade_desc": "Warm mulled spiced plum"}
                    }
                },
                {
                    "upper": {"name": "Cable Knit Fisherman Cardigan", "fabric": "Heft British Shetland Wool", "silhouette": "Horn Button Boxy Silhouette"},
                    "bottom": {"name": "Straight Leg Corduroy Pants", "fabric": "Fine Needlecord Velvet Touch", "silhouette": "High-Rise Ankle Skim"},
                    "shoes": {"name": "Shearling-Lined Leather Booties", "material": "Waxed Leather with Merino Shearling", "silhouette": "Low Ankle Lace-Up"},
                    "jewellery": {
                        "necklace": {"name": "Raw Baroque Stone Pendant", "metal": "Irregular Mineral Stone on Fine Chain"},
                        "earrings": {"name": "Thick Chunky Huggie Hoops", "metal": "D-Shape Solid Metal"},
                        "lipstick_tint": {"name": "Warm Chestnut Nude Stain", "finish": "Balm-In-Stain Sheer Pigment", "shade_desc": "Effortless warm chestnut undertone"}
                    }
                }
            ]
        },
        "monsoon": {
            "male": [
                {
                    "upper": {"name": "Water-Repellent Overshirt over Pima Tee", "fabric": "Treated DWR Technical Poplin", "silhouette": "Snap-Button Lightweight Utility"},
                    "bottom": {"name": "Quick-Dry Stretch Chino Pants", "fabric": "Water-Resistant Technical Twill", "silhouette": "Ankle-Crop Clean Fit"},
                    "shoes": {"name": "Waterproof Leather Chelsea Boots", "material": "Silicone-Treated Waterproof Calf", "silhouette": "Vibram Commando Lug Sole"},
                    "jewellery": {
                        "rings": {"name": "Tungsten Carbide Band", "metal": "Scratch-Resistant Tungsten"},
                        "earrings": {"name": "Black Titanium Stud", "metal": "Anodized Black Titanium"},
                        "watch": {"name": "Aquaracer 300M Diver", "dial": "Deep Navy / Slate Sunray on Rubber"}
                    }
                },
                {
                    "upper": {"name": "Treated Poplin Long-Sleeve Shirt", "fabric": "Breathable Water-Shedding Poplin", "silhouette": "Convertible Collar Utility"},
                    "bottom": {"name": "Tapered Performance Cargo Trousers", "fabric": "Matte Stretch Ripstop", "silhouette": "Articulated Knee Taper"},
                    "shoes": {"name": "All-Weather Leather Trainers", "material": "Gore-Tex Lined Napa Leather", "silhouette": "Waterproof Modern Runner"},
                    "jewellery": {
                        "rings": {"name": "Matte Brushed Titanium Ring", "metal": "Corrosion-Proof Titanium"},
                        "earrings": {"name": "Sleek Industrial Huggie", "metal": "Gunmetal PVD Metal"},
                        "watch": {"name": "Tactical Field Chronograph", "dial": "Matte Ceramic Bezel on Silicone"}
                    }
                },
                {
                    "upper": {"name": "Breathable Technical Harrington Jacket", "fabric": "Micro-Porous Weather Shield", "silhouette": "Stand Collar Zip Harrington"},
                    "bottom": {"name": "Dark Indigo Water-Resistant Denim", "fabric": "DWR Treated Heavy Japanese Twill", "silhouette": "Slim Tapered Clean Hem"},
                    "shoes": {"name": "Waxed Suede Chukka Boots", "material": "Treated Waterproof Suede", "silhouette": "Two-Eyelet Ankle Chukka"},
                    "jewellery": {
                        "rings": {"name": "Engraved Minimalist Signet", "metal": "Marine-Grade Steel / Bronze"},
                        "earrings": {"name": "Micro Geometric Bar Stud", "metal": "Surgical Stainless Steel"},
                        "watch": {"name": "Seafarer Horology on Leather", "dial": "Luminous Dial with Water-Lock Crown"}
                    }
                },
                {
                    "upper": {"name": "Lightweight Technical Knit Polo", "fabric": "Quick-Dry Moisture Wicking Pique", "silhouette": "Clean Minimal Placket"},
                    "bottom": {"name": "Cropped Technical Commuter Pants", "fabric": "Water-Repellent Stretch Twill", "silhouette": "Cropped Above-Ankle"},
                    "shoes": {"name": "Sleek Rainproof Derby Shoes", "material": "High-Shine Rubberized Leather", "silhouette": "Storm-Welted Lug Sole"},
                    "jewellery": {
                        "rings": {"name": "Dual-Tone Metal Band", "metal": "Brushed and Polished Contrast"},
                        "earrings": {"name": "Small Beveled Huggie", "metal": "Low-Profile Platinum / Gold Tone"},
                        "watch": {"name": "Chronograph with Dark Sub-Dials", "dial": "High-Legibility Dial on Tropic Rubber"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Belted Trench-Inspired Tunic Blouse", "fabric": "Water-Repellent Cotton Gabardine", "silhouette": "Double-Breasted Tie Waist"},
                    "bottom": {"name": "Ankle-Crop Cigarette Trousers", "fabric": "Stretch Quick-Dry Compact Crepe", "silhouette": "Tailored Slim Crop (Splash-Proof)"},
                    "shoes": {"name": "Glossy Chelsea Rain Booties", "material": "Waterproof Vulcanized Gloss Rubber", "silhouette": "Sleek Ankle Silhouette"},
                    "jewellery": {
                        "necklace": {"name": "Waterproof Gold PVD Chain", "metal": "Non-Tarnish PVD Coated Gold"},
                        "earrings": {"name": "Chunky Waterproof Huggie Drops", "metal": "Tarnish-Resistant Titanium Base"},
                        "lipstick_tint": {"name": "Waterproof Longwear Lip Ink", "finish": "Long-Lasting Matte Ink Stain", "shade_desc": "Smudge-proof vibrant berry / peach flush"}
                    }
                },
                {
                    "upper": {"name": "Silky Poplin Shirt with Lightweight Capelet", "fabric": "Weather-Treated Mercerized Poplin", "silhouette": "Structured Drape with Collar"},
                    "bottom": {"name": "Tailored Water-Repellent Culottes", "fabric": "Compact Crepe with DWR Finish", "silhouette": "High-Waist Wide Crop"},
                    "shoes": {"name": "Treated Leather Lug-Sole Loafers", "material": "Water-Sealed Box Leather", "silhouette": "Platform Bit Loafer"},
                    "jewellery": {
                        "necklace": {"name": "Geometric Pendant on Steel Rope", "metal": "Water-Safe Polished Pendant"},
                        "earrings": {"name": "Sleek Teardrop Ear Climbers", "metal": "Ear Wire Sculptural Climbers"},
                        "lipstick_tint": {"name": "Hydra-Gel Stained Lip Tint", "finish": "Rain-Resistant Gel Satin", "shade_desc": "Crisp juicy rose flush that lasts through humidity"}
                    }
                },
                {
                    "upper": {"name": "Technical Knit Mock-Neck Layer", "fabric": "Ultra-Fine Quick-Dry Merino Modal", "silhouette": "Sleek Ribbed Shell"},
                    "bottom": {"name": "Coated Denim Slim Pants", "fabric": "Wax-Coated Water-Repellent Stretch Denim", "silhouette": "Skinny Ankle Tuck"},
                    "shoes": {"name": "Waterproof Suede Combat Ankle Boots", "material": "Sealed Italian Hydro-Suede", "silhouette": "Lace-Up with Inner Zip"},
                    "jewellery": {
                        "necklace": {"name": "Layered Coin Charms", "metal": "PVD Non-Tarnish Gold / Silver"},
                        "earrings": {"name": "Minimalist Oval Link Hoops", "metal": "Elongated Modern Link"},
                        "lipstick_tint": {"name": "Velvet Lip Cushion Stain", "finish": "Water-Locked Powder Velvet", "shade_desc": "Rich terracotta / plum humidity-resistant shade"}
                    }
                },
                {
                    "upper": {"name": "Cropped Rain-Shield Utility Jacket over Rib Tank", "fabric": "Technical Matte Gabardine", "silhouette": "Cinched Bungee Waist"},
                    "bottom": {"name": "Fluid Pleated Midi Skirt in Quick-Dry Satin", "fabric": "Water-Resistant Technical Satin", "silhouette": "Sunray Pleated Flow"},
                    "shoes": {"name": "Matte Lug-Sole Chunky Derby Shoes", "material": "Rubberized Calfskin", "silhouette": "Platform Lug Derby"},
                    "jewellery": {
                        "necklace": {"name": "Modern Toggle Clasp Choker", "metal": "Chunky Steel Clasp Detail"},
                        "earrings": {"name": "Molten Hoop Earrings", "metal": "Sculptural Liquid Gold Texture"},
                        "lipstick_tint": {"name": "Hydrating Nude Tint Serum", "finish": "Non-Sticky Satin Serum Tint", "shade_desc": "Nourishing rain-proof luminous petal tone"}
                    }
                }
            ]
        },
        "spring_autumn": {
            "male": [
                {
                    "upper": {"name": "Suede Overshirt over Slub Cotton Tee", "fabric": "Supple Goat Suede & Pima Cotton", "silhouette": "Western Point Yoke Overshirt"},
                    "bottom": {"name": "Slim Straight Garment-Dyed Chinos", "fabric": "Peach-Finished Cotton Twill", "silhouette": "Mid-Rise Clean Taper"},
                    "shoes": {"name": "Suede Penny Loafers", "material": "Cashmere Suede with Leather Sole", "silhouette": "Unlined Flexible Loafer"},
                    "jewellery": {
                        "rings": {"name": "Hammered Signet Ring", "metal": "Satin 18k Warm Gold"},
                        "earrings": {"name": "Minimalist Micro Hoop", "metal": "Brushed Warm Alloy"},
                        "watch": {"name": "Vintage Chronograph on Tan Calfskin", "dial": "Champagne Sunburst Dial"}
                    }
                },
                {
                    "upper": {"name": "Merino Wool Knit Polo", "fabric": "Extra-Fine 100% Australian Merino", "silhouette": "Three-Button Ribbed Hem"},
                    "bottom": {"name": "Pleated Wool-Blend Flannel Slacks", "fabric": "Tropical Weight Worsted Wool", "silhouette": "Single Pleat Relaxed Drape"},
                    "shoes": {"name": "Burnished Leather Chelsea Boots", "material": "Hand-Polished Crust Calfskin", "silhouette": "Sleek Almond Toe"},
                    "jewellery": {
                        "rings": {"name": "Engraved Horizon Band", "metal": "Satin Metal Band"},
                        "earrings": {"name": "Clean Stud in Semi-Precious Inlay", "metal": "Onyx / Tiger Eye Stud"},
                        "watch": {"name": "Slim Dress Watch with Roman Indices", "dial": "Textured Guilloche Dial"}
                    }
                },
                {
                    "upper": {"name": "Heavy Cotton Chore Jacket over Oxford Shirt", "fabric": "12oz Cotton Duck Canvas & Oxford Weave", "silhouette": "Three-Pocket Workwear Classic"},
                    "bottom": {"name": "Japanese Indigo Raw Denim Jeans", "fabric": "13.5oz Kurabo Mill Raw Denim", "silhouette": "Classic Regular Taper"},
                    "shoes": {"name": "Handcrafted Leather Service Boots", "material": "Chromexcel Steerhide", "silhouette": "Cap-Toe Stitched Ankle Boot"},
                    "jewellery": {
                        "rings": {"name": "Coin Inset Signet", "metal": "Antique Finished Alloy"},
                        "earrings": {"name": "Subtle Huggie Hoop", "metal": "Matte Low-Reflectance"},
                        "watch": {"name": "Heritage Field Watch with Leather Cuff", "dial": "Olive / Cream Military Dial"}
                    }
                },
                {
                    "upper": {"name": "Fine-Ribbed Half-Zip Sweater", "fabric": "Silk & Cashmere Lightweight Blend", "silhouette": "Funnel Neck Metallic Zip"},
                    "bottom": {"name": "Tailored Gabardine Trousers", "fabric": "Virgin Wool Gabardine", "silhouette": "Contemporary Flat Front"},
                    "shoes": {"name": "Suede Monk Strap Shoes", "material": "Buttery Italian Snu-Suede", "silhouette": "Double Buckle Brass Closure"},
                    "jewellery": {
                        "rings": {"name": "Beveled Square Band", "metal": "Modern High-Precision Metal"},
                        "earrings": {"name": "Micro Ball Ear Stud", "metal": "Hypoallergenic Titanium"},
                        "watch": {"name": "Minimalist Horology on Alligator Strap", "dial": "Clean Slate / Silver Minimal Dial"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Silk Crepe de Chine Button-Down", "fabric": "100% Pure Mulberry Silk Crepe", "silhouette": "Fluid Pointed Collar Blouse"},
                    "bottom": {"name": "High-Waist Pleated Wide-Leg Pants", "fabric": "Heavy Drape Viscose Crepe", "silhouette": "High-Rise Floor-Grazing"},
                    "shoes": {"name": "Pointed-Toe Suede Kitten Heels", "material": "Velvety Kid Suede", "silhouette": "50mm Flattering Kitten Heel"},
                    "jewellery": {
                        "necklace": {"name": "Layered Paperclip Chain with Pearl", "metal": "Dainty Links with Floating Keshi Pearl"},
                        "earrings": {"name": "Textured Ripple Huggies", "metal": "18k Warm Gold or Icy White Gold"},
                        "lipstick_tint": {"name": "Velvet Rosewood Lip Tint", "finish": "Satin Velvet Cushion Tint", "shade_desc": "Warm rosewood with luminous depth"}
                    }
                },
                {
                    "upper": {"name": "Fine-Gauge Cashmere Crewneck Sweater", "fabric": "Pure Featherlight Mongolian Cashmere", "silhouette": "Relaxed Shoulder Drop"},
                    "bottom": {"name": "Satin Bias-Cut Midi Skirt", "fabric": "Heavy Sandwashed Silk Satin", "silhouette": "Fluid Bias Drape Ankle Skim"},
                    "shoes": {"name": "Leather Knee-High Slouch Boots", "material": "Supple French Calfskin", "silhouette": "Soft Fold Slouch Boot"},
                    "jewellery": {
                        "necklace": {"name": "Molten Coin Pendant Necklace", "metal": "Ancient Coin Replica on Cable Chain"},
                        "earrings": {"name": "Graduated Pearl Drop Earrings", "metal": "Natural Baroque Pearls on Wire"},
                        "lipstick_tint": {"name": "Warm Terracotta / Berry Petal", "finish": "Dewy Luminous Strobe", "shade_desc": "Rich floral petal stain with subtle golden sheen"}
                    }
                },
                {
                    "upper": {"name": "Cropped Double-Breasted Trench Jacket", "fabric": "Weather-Resistant Cotton Twill", "silhouette": "Raglan Sleeve Cropped Trench"},
                    "bottom": {"name": "High-Rise Tailored Wool Culottes", "fabric": "Fine Worsted Wool Crepe", "silhouette": "Sharp Center Crease Crop"},
                    "shoes": {"name": "Almond-Toe Leather Loafers with Hardware", "material": "Glossy Italian Leather", "silhouette": "Equestrian Horsebit Detail"},
                    "jewellery": {
                        "necklace": {"name": "Snake Chain Choker with Toggle", "metal": "Fluid Liquid Metal Collar"},
                        "earrings": {"name": "Sculptural Chunky Tear Studs", "metal": "Hollow Droplet Shapes"},
                        "lipstick_tint": {"name": "Spiced Peach Satin Cushion", "finish": "Hydrating Velvet Stained Cream", "shade_desc": "Subtle autumn spice with fresh glow"}
                    }
                },
                {
                    "upper": {"name": "Draped Cowl-Neck Silk Knit", "fabric": "Silk & Cashmere Fine Jersey", "silhouette": "Fluid Cowl Draping"},
                    "bottom": {"name": "Tailored Column Pencil Skirt with Front Slit", "fabric": "Stretch Wool Melange", "silhouette": "High-Waist Clean Column"},
                    "shoes": {"name": "Sculpted Heel Leather Mules", "material": "Buttery Glove Calfskin", "silhouette": "Architectural Kitten Heel"},
                    "jewellery": {
                        "necklace": {"name": "Baroque Freshwater Pearl Strand", "metal": "Knotted Silk Thread with Gold Clasp"},
                        "earrings": {"name": "Hammered Disc Studs", "metal": "Concave Light-Bending Discs"},
                        "lipstick_tint": {"name": "Caramel Nude Gloss Lip Oil", "finish": "Nutrient Gloss Serum Strobe", "shade_desc": "Plumping warm caramel nude glow"}
                    }
                }
            ]
        }
    },
    "formal": {
        "summer": {
            "male": [
                {
                    "upper": {"name": "Unstructured Tropical Wool Blazer & Linen Shirt", "fabric": "Super 130s Lightweight Wool & French Linen", "silhouette": "Neapolitan Soft Shoulder Blazer"},
                    "bottom": {"name": "Matching Flat-Front Tropical Wool Trousers", "fabric": "High-Twist Breathable Fresco Wool", "silhouette": "Clean Tapered Trouser"},
                    "shoes": {"name": "Hand-Polished Leather Bit Loafers", "material": "Full-Grain Box Calf with Brass Bit", "silhouette": "Goodyear-Welted Loafer"},
                    "jewellery": {
                        "rings": {"name": "Brushed Gold Signet Ring", "metal": "18k Warm Gold or White Gold"},
                        "earrings": {"name": "Micro Beveled Stud", "metal": "Subtle Low-Profile Metal Stud"},
                        "watch": {"name": "Ultra-Slim Chronometer with White Dial", "dial": "Guilloche Enamel on Leather"}
                    }
                },
                {
                    "upper": {"name": "Crisp Sea-Island Cotton Dress Shirt & Silk Knit Tie", "fabric": "140/2 Ply Sea Island Cotton & Silk", "silhouette": "Semi-Spread Collar Tailored"},
                    "bottom": {"name": "Lightweight Wool Trousers with Side Adjusters", "fabric": "High-Twist Fresco Wool", "silhouette": "Gurkha Waistband Tailored"},
                    "shoes": {"name": "Wholecut Calfskin Oxford Shoes", "material": "Single-Piece Crust Leather", "silhouette": "Sleek Closed-Lacing Oxford"},
                    "jewellery": {
                        "rings": {"name": "Satin Finish Platinum / Gold Band", "metal": "High-Precision Clean Band"},
                        "earrings": {"name": "Minimalist Huggie Hoop", "metal": "Matte Finished Metal"},
                        "watch": {"name": "Dress Horology on Alligator Strap", "dial": "Roman Numerals with Sapphire Glass"}
                    }
                },
                {
                    "upper": {"name": "Solaro Silk-Linen Blend Suit Jacket", "fabric": "Silk, Linen & Wool Solaro Weave", "silhouette": "Two-Button Peak Lapel"},
                    "bottom": {"name": "Matching Solaro Tailored Trousers", "fabric": "Iridescent Solaro Weave", "silhouette": "Clean Double Pleat Taper"},
                    "shoes": {"name": "Handcrafted Leather Monk Straps", "material": "Museum Calfskin Leather", "silhouette": "Single Brass Buckle Monk"},
                    "jewellery": {
                        "rings": {"name": "Classic Oval Signet", "metal": "Heavyweight Polished Metal"},
                        "earrings": {"name": "Subtle Geometric Stud", "metal": "Titanium Stud"},
                        "watch": {"name": "Vintage Chronometer with Gold Bezel", "dial": "Cream Dial on Dark Brown Calf"}
                    }
                },
                {
                    "upper": {"name": "Spread Collar Poplin Shirt & Linen Waistcoat", "fabric": "Egyptian Giza Cotton & Irish Linen", "silhouette": "Tailored Five-Button Vest"},
                    "bottom": {"name": "Crisp Poplin Weave Dress Trousers", "fabric": "Wool-Silk Blend Tropical Poplin", "silhouette": "Modern Flat-Front Hem"},
                    "shoes": {"name": "Perforated Quarter-Brogue Derbies", "material": "Hand-Burnished French Calf", "silhouette": "Elegant Chiseled Toe"},
                    "jewellery": {
                        "rings": {"name": "Faceted Edge Band", "metal": "Dual Finish Precious Metal"},
                        "earrings": {"name": "Low-Profile Disc Stud", "metal": "Surgical Grade Titanium"},
                        "watch": {"name": "Small Seconds Dress Horology", "dial": "Sunburst Dial with Blued Steel Hands"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Tailored Linen-Silk Suiting Blazer", "fabric": "60% Irish Linen & 40% Raw Silk", "silhouette": "Single-Breasted Sculpted Blazer"},
                    "bottom": {"name": "High-Rise Cigarette Slacks in Linen-Silk", "fabric": "Matching Breathable Silk Weave", "silhouette": "Ankle-Grazing Pressed Crease"},
                    "shoes": {"name": "Pointed D'Orsay Leather Pumps", "material": "Buttery Glove Calfskin", "silhouette": "75mm Elegant Stiletto / Block Heel"},
                    "jewellery": {
                        "necklace": {"name": "Geometric Gold / Silver Collar Choker", "metal": "Structured Solid Torque Collar"},
                        "earrings": {"name": "Pavé Diamond / Zirconia Huggie Drops", "metal": "Micro-Pavé Set in Warm/Cool Metal"},
                        "lipstick_tint": {"name": "Satin Coral / Rose Executive Tint", "finish": "Hydrating Satin Cream Finish", "shade_desc": "Polished boardroom-ready color"}
                    }
                },
                {
                    "upper": {"name": "Silk Georgette Lavallière Pussy-Bow Blouse", "fabric": "100% Pure Mulberry Silk Georgette", "silhouette": "Fluid Neck Tie Bow Blouse"},
                    "bottom": {"name": "High-Waist Tailored Crepe Pencil Skirt", "fabric": "Italian Double-Crepe Wool", "silhouette": "Midi Length Concealed Slit"},
                    "shoes": {"name": "Slingback Leather Kitten Pumps", "material": "Gloss Patent & Smooth Leather", "silhouette": "Chiseled Pointed Slingback"},
                    "jewellery": {
                        "necklace": {"name": "Single Solitaire Gem on Delicate Link", "metal": "Four-Prong Gemstone Setting"},
                        "earrings": {"name": "Sculptural Pearl Wire Drops", "metal": "Akoya Pearl on Fine Wire"},
                        "lipstick_tint": {"name": "Velvet Nude Rose Elegance", "finish": "Weightless Velvet Stain", "shade_desc": "Sophisticated understated lip harmony"}
                    }
                },
                {
                    "upper": {"name": "Sleeveless Tailored Wool Crepe Shell & Jacket", "fabric": "Triple-Crepe Lightweight Wool", "silhouette": "Minimalist High Jewel Neckline"},
                    "bottom": {"name": "Wide-Leg Floor-Length Suiting Trousers", "fabric": "Matching Crepe Fluid Drape", "silhouette": "Double Deep Pleat Wide Leg"},
                    "shoes": {"name": "Block-Heel Leather Mules", "material": "Fine Calf Leather", "silhouette": "Square-Toe Architectural Mule"},
                    "jewellery": {
                        "necklace": {"name": "Liquid Metal Herringbone Chain", "metal": "High Luster Flexible Chain"},
                        "earrings": {"name": "Molten Gold / Platinum Studs", "metal": "Organic Hand-Cast Texture"},
                        "lipstick_tint": {"name": "Spiced Terracotta / Crimson Satin", "finish": "Long-Wearing Satin Stain", "shade_desc": "Commanding executive presence"}
                    }
                },
                {
                    "upper": {"name": "Double-Breasted Silk Vest as Top", "fabric": "Raw Silk Dupioni", "silhouette": "Fitted Sleeveless Waistcoat Top"},
                    "bottom": {"name": "Matching Silk-Linen Fluid Slacks", "fabric": "Silk & Linen Summer Weave", "silhouette": "Relaxed Tailored Fall"},
                    "shoes": {"name": "Ankle-Strap Minimalist Dress Heels", "material": "Nappa Leather Straps", "silhouette": "Delicate Two-Strap Heel"},
                    "jewellery": {
                        "necklace": {"name": "Layered Fine Cable & Pendant", "metal": "Multi-Length Delicate Strands"},
                        "earrings": {"name": "Tapered Baguette Studs", "metal": "Channel Set Baguette Stones"},
                        "lipstick_tint": {"name": "Petal Blush Satin Strobe", "finish": "Hydra-Gloss Stained Sheen", "shade_desc": "Fresh daylight executive luminosity"}
                    }
                }
            ]
        },
        "winter": {
            "male": [
                {
                    "upper": {"name": "Double-Breasted Heavy Wool Flannel Suit Jacket", "fabric": "100% British Wool Flannel (380g)", "silhouette": "Six-on-Two Peak Lapel"},
                    "bottom": {"name": "Matching Pleated Wool Flannel Trousers", "fabric": "Worsted Flannel with Cuffed Hem", "silhouette": "High-Waist Deep Pleat"},
                    "shoes": {"name": "Hand-Waxed Leather Balmoral Oxford Boots", "material": "Full-Grain Calfskin & Suede Shaft", "silhouette": "Goodyear-Welted Dress Boot"},
                    "jewellery": {
                        "rings": {"name": "Onyx Inset Gold Signet", "metal": "18k Heavy Gold with Black Onyx"},
                        "earrings": {"name": "Sleek Matte Huggie", "metal": "Brushed Dark Metal"},
                        "watch": {"name": "Heritage Automatic on Dark Alligator", "dial": "Deep Midnight / Enamel Dial"}
                    }
                },
                {
                    "upper": {"name": "Cashmere Overcoat over Three-Piece Tailored Suit", "fabric": "100% Pure Italian Cashmere (480g)", "silhouette": "Structured Chesterfield Coat"},
                    "bottom": {"name": "Worsted Wool Tailored Dress Trousers", "fabric": "Super 150s Merino Wool", "silhouette": "Razor-Sharp Creased Leg"},
                    "shoes": {"name": "Mirror-Polished Oxford Cap-Toes", "material": "Glacé Calfskin with Oak Bark Sole", "silhouette": "Sleek Formal Dress Cap-Toe"},
                    "jewellery": {
                        "rings": {"name": "Faceted Platinum / Gold Band", "metal": "Heft Precious Metal"},
                        "earrings": {"name": "Subtle Stud in Titanium", "metal": "Polished Flush Setting"},
                        "watch": {"name": "Gold Bezel Chronometer", "dial": "Ivory Dial with Roman Numerals"}
                    }
                },
                {
                    "upper": {"name": "Fine Cashmere Rollneck under Tweed Tailored Blazer", "fabric": "Pure Cashmere & Scottish Donegall Tweed", "silhouette": "Notch Lapel Soft Structure"},
                    "bottom": {"name": "Heavy Cavalry Twill Trousers", "fabric": "Pure Wool Cavalry Twill", "silhouette": "Tailored Straight Cut"},
                    "shoes": {"name": "Full-Brogue Leather Derby Shoes", "material": "Burnished Scotch Grain Calf", "silhouette": "Sturdy Formal Wingtip"},
                    "jewellery": {
                        "rings": {"name": "Engraved Monogram Signet", "metal": "Warm Alloy Signet"},
                        "earrings": {"name": "Micro Beveled Stud", "metal": "Surgical Titanium"},
                        "watch": {"name": "Pilot Horology with Brown Leather Strap", "dial": "Dark Dial with Gold Accents"}
                    }
                },
                {
                    "upper": {"name": "Tailored Velvet Evening Blazer & Tuxedo Shirt", "fabric": "Cotton Velvet & Pleated Poplin", "silhouette": "Shawl Lapel Velvet Tuxedo"},
                    "bottom": {"name": "Black Tuxedo Trousers with Satin Side Stripe", "fabric": "Barathea Wool & Silk Satin", "silhouette": "Formal Black Tie Tailoring"},
                    "shoes": {"name": "Patent Leather Evening Oxford Pumps", "material": "Gloss Patent Calfskin", "silhouette": "Grosgrain Bow Evening Shoe"},
                    "jewellery": {
                        "rings": {"name": "Solid Gold / Platinum Pinky Ring", "metal": "Mirror-Finish Heavy Precious Metal"},
                        "earrings": {"name": "Diamond / Moissanite Flush Stud", "metal": "Solitaire Stud Setting"},
                        "watch": {"name": "Ultra-Thin Black-Tie Dress Horology", "dial": "Onyx Minimalist Dial"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Tailored Cashmere-Wool Wrap Coat & Silk Blouse", "fabric": "Double-Faced Cashmere & Heavy Silk", "silhouette": "Structured Belted Silhouette"},
                    "bottom": {"name": "Wide-Leg Wool Flannel Trousers", "fabric": "Italian Virgin Wool Flannel", "silhouette": "High-Waist Deep Front Pleats"},
                    "shoes": {"name": "Pointed-Toe Leather Knee-High Boots", "material": "Glove Calfskin with Leather Sole", "silhouette": "Sculpted Architectural Heel"},
                    "jewellery": {
                        "necklace": {"name": "Chunky Curb Chain with Diamond Pavé Clasp", "metal": "Heavy High-Luster Chain"},
                        "earrings": {"name": "Statement Molten Metal Drop Earrings", "metal": "Bold Light-Reflective Casts"},
                        "lipstick_tint": {"name": "Deep Velvet Bordeaux Wine Tint", "finish": "Pigment-Rich Velvet Matte", "shade_desc": "Sophisticated dramatic winter definition"}
                    }
                },
                {
                    "upper": {"name": "Wool Crepe Tuxedo Blazer with Satin Lapels", "fabric": "Heavy Wool Crepe & Silk Duchesse Satin", "silhouette": "Peak Lapel Cigarette Fit"},
                    "bottom": {"name": "Matching Satin-Stripe Tuxedo Cigarette Pants", "fabric": "Barathea Wool with Silk Side Stripe", "silhouette": "Slim Ankle-Grazing Cut"},
                    "shoes": {"name": "Patent Leather Pointed Pumps", "material": "High-Gloss Mirror Patent Calf", "silhouette": "Classic 85mm Stiletto"},
                    "jewellery": {
                        "necklace": {"name": "Diamond / Crystal Rivière Choker", "metal": "Continuous Prong-Set Sparkling Stones"},
                        "earrings": {"name": "Cascading Crystal Chandelier Drops", "metal": "Art-Deco Linear Drop Earrings"},
                        "lipstick_tint": {"name": "Crimson Ruby Velvet Sensation", "finish": "Longwear High-Vibrancy Velvet", "shade_desc": "Timeless iconic red carpet ruby"}
                    }
                },
                {
                    "upper": {"name": "Cashmere Knit Mock-Neck under Structured Suit", "fabric": "100% Grade-A Mongolian Cashmere", "silhouette": "Form-Fitting Luxurious Base"},
                    "bottom": {"name": "Tailored Column Slacks with Front Seam", "fabric": "Worsted Wool Stretch Melange", "silhouette": "Pin-Tuck Elongating Line"},
                    "shoes": {"name": "Square-Toe Heeled Ankle Booties", "material": "Polished Spazzolato Box Leather", "silhouette": "Block Heel Minimalist Silhouette"},
                    "jewellery": {
                        "necklace": {"name": "Thick Herringbone Fluid Choker", "metal": "High-Gloss Metal Liquid Collar"},
                        "earrings": {"name": "Chunky Quad-Hoop Stacking Earrings", "metal": "Stacked Intertwined Rings"},
                        "lipstick_tint": {"name": "Spiced Plum Velvet Matte Tint", "finish": "Deep Hydrating Satin Matte", "shade_desc": "Rich plum depth harmonized with skin undertone"}
                    }
                },
                {
                    "upper": {"name": "Belted Trench Blazer in Heavy Wool Crepe", "fabric": "Triple-Woven Heavy Wool Crepe", "silhouette": "Self-Belted Double-Breasted"},
                    "bottom": {"name": "Matching Tailored Midi Pencil Skirt", "fabric": "Structured Wool Crepe", "silhouette": "Clean Formal Midi Length"},
                    "shoes": {"name": "Leather Slingback Block Pumps", "material": "Italian Burnished Calf", "silhouette": "Pointed Toe Covered Block Heel"},
                    "jewellery": {
                        "necklace": {"name": "Baroque Pearl & Gold Link Collar", "metal": "Mixed Media Organic Luxury"},
                        "earrings": {"name": "Sculptural Fan Earrings", "metal": "Textured Radial Lines"},
                        "lipstick_tint": {"name": "Rich Mocha Rose Satin Lip", "finish": "Cushion Satin Longwear", "shade_desc": "Earthy rose with luxurious warm/cool neutrality"}
                    }
                }
            ]
        },
        "monsoon": {
            "male": [
                {
                    "upper": {"name": "Water-Repellent Wool-Blend Travel Blazer & Shirt", "fabric": "Loro Piana Rain & Wind Technical Wool", "silhouette": "Tailored Two-Button Traveler"},
                    "bottom": {"name": "Matching Water-Resistant Wool Trousers", "fabric": "DWR Treated High-Twist Wool", "silhouette": "Clean Modern Straight"},
                    "shoes": {"name": "Storm-Welted Leather Oxford Shoes", "material": "Water-Sealed French Calfskin", "silhouette": "Dainite Rubber Studded Sole"},
                    "jewellery": {
                        "rings": {"name": "Brushed Cobalt Ring", "metal": "Corrosion-Proof Heavy Cobalt"},
                        "earrings": {"name": "Titanium Micro Stud", "metal": "Hypoallergenic Titanium"},
                        "watch": {"name": "Luxury Diver Horology 200M", "dial": "Dark Sunray Dial with Water Seal"}
                    }
                },
                {
                    "upper": {"name": "Single-Breasted Mackintosh Trench over Suit", "fabric": "Bonded Waterproof Cotton Gabardine", "silhouette": "Fly-Front Clean Silhouette"},
                    "bottom": {"name": "Tailored Stain-Resistant Dress Slacks", "fabric": "Nanotech Treated Wool Twill", "silhouette": "Cuffed Ankle Clean Line"},
                    "shoes": {"name": "Waxed Leather Chelsea Dress Boots", "material": "Water-Resistant Crust Leather", "silhouette": "Elastic Gusset Rain Dress Boot"},
                    "jewellery": {
                        "rings": {"name": "Signet with Sapphire / Topaz Inset", "metal": "Heavy Alloy with Gem Inset"},
                        "earrings": {"name": "Sleek Matte Huggie Ring", "metal": "PVD Coated Metal"},
                        "watch": {"name": "Chronograph on Waterproof Alligator", "dial": "High-Contrast Sub-Dials"}
                    }
                },
                {
                    "upper": {"name": "Water-Repellent Poplin Spread Collar Shirt", "fabric": "100% Giza Cotton with DWR Treatment", "silhouette": "French Cuff Tailored Placket"},
                    "bottom": {"name": "High-Twist Fresco Wool Slacks", "fabric": "Crisp Crease-Resistant Fresco", "silhouette": "Double Pleated Trouser"},
                    "shoes": {"name": "Rubber-Soled Leather Monk Straps", "material": "Polished Box Leather", "silhouette": "Double Brass Buckle Weatherproof"},
                    "jewellery": {
                        "rings": {"name": "Faceted Platinum / Gold Band", "metal": "Satin Precision Metal"},
                        "earrings": {"name": "Minimalist Disc Stud", "metal": "Surgical Steel"},
                        "watch": {"name": "Fluted Bezel Horology with Screw-Down Crown", "dial": "Champagne / Slate Dial"}
                    }
                },
                {
                    "upper": {"name": "Unstructured Performance Wool Suit Jacket", "fabric": "Breathable Rain-Shield Stretch Wool", "silhouette": "Modern Slim Lapel"},
                    "bottom": {"name": "Matching Performance Wool Slacks", "fabric": "Quick-Dry Stretch Worsted Wool", "silhouette": "Ankle-Crop Clean Line"},
                    "shoes": {"name": "High-Shine Weatherproof Oxford Brogues", "material": "Water-Sealed Patent Leather", "silhouette": "Wingtip Brogue on Dainite"},
                    "jewellery": {
                        "rings": {"name": "Brushed Steel Pinky Ring", "metal": "Solid Precision Alloy"},
                        "earrings": {"name": "Geometric Minimal Stud", "metal": "Titanium Setting"},
                        "watch": {"name": "Dress Horology with Stainless Steel Bracelet", "dial": "Luminous Dial"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Water-Repellent Double-Breasted Trench Jacket", "fabric": "Treated Compact Cotton Gabardine", "silhouette": "Structured Belted Silhouette"},
                    "bottom": {"name": "Tailored Ankle-Crop Crepe Trousers", "fabric": "Water-Resistant Compact Crepe", "silhouette": "Slim Pressed Crease Ankle Crop"},
                    "shoes": {"name": "Waterproof Leather Block-Heel Pumps", "material": "Hydro-Treated Nappa Leather", "silhouette": "Commando Rubber Inset Sole"},
                    "jewellery": {
                        "necklace": {"name": "Waterproof Gold PVD Torque Choker", "metal": "Seamless Non-Tarnish Gold PVD"},
                        "earrings": {"name": "Chunky Non-Tarnish Hoop Earrings", "metal": "Titanium Core 18k Gold Plated"},
                        "lipstick_tint": {"name": "Rainproof Velvet Tint Stain", "finish": "Longwear Waterproof Velvet", "shade_desc": "Transfer-proof berry / coral vibrancy"}
                    }
                },
                {
                    "upper": {"name": "Silk Poplin Button-Down under Water-Shed Blazer", "fabric": "Mercerized Poplin & Technical Crepe", "silhouette": "Sharp Tailored Shoulder"},
                    "bottom": {"name": "Tailored High-Waist Pencil Skirt", "fabric": "Stain-Resistant Stretch Wool Blend", "silhouette": "Midi Length Center Slit"},
                    "shoes": {"name": "Glossy Ankle Rain Dress Boots", "material": "Polished Vulcanized Rubber with Patent Look", "silhouette": "Pointed Toe Block Heel"},
                    "jewellery": {
                        "necklace": {"name": "Modern Bar Pendant on Stainless Link", "metal": "Corrosion-Proof Sleek Setting"},
                        "earrings": {"name": "Minimalist Teardrop Ear Climbers", "metal": "Non-Tarnish Precious Metal"},
                        "lipstick_tint": {"name": "Hydra-Gel Stained Lip Tint", "finish": "Transfer-Proof High-Stain Sheen", "shade_desc": "Vibrant and impervious to weather"}
                    }
                },
                {
                    "upper": {"name": "High-Collar Silk Shell & Single-Breasted Blazer", "fabric": "Heavy Silk Crepe & Technical Wool", "silhouette": "Minimalist Jewel Neckline"},
                    "bottom": {"name": "Fluid Tailored Wide-Leg Splash-Proof Slacks", "fabric": "Nanotech Water-Repellent Worsted Wool", "silhouette": "High-Rise Floor Skim"},
                    "shoes": {"name": "Chunky Lug-Sole Leather Bit Loafers", "material": "Weather-Sealed Calfskin", "silhouette": "Platform Bit Loafer with Rubber Lug"},
                    "jewellery": {
                        "necklace": {"name": "Liquid Metal Snake Chain Collar", "metal": "High Luster Water-Safe Coating"},
                        "earrings": {"name": "Molten Texture Round Studs", "metal": "Cast Stainless Alloy with Heavy Gold / Silver PVD"},
                        "lipstick_tint": {"name": "Spiced Terracotta Matte Lip Ink", "finish": "12-Hour Longwear Velvet Tint", "shade_desc": "Rich, non-drying earth tone"}
                    }
                },
                {
                    "upper": {"name": "Belted Safari Suiting Jacket in Technical Linen", "fabric": "Water-Repellent Linen-Poly Weave", "silhouette": "Four-Pocket Safari with Self-Belt"},
                    "bottom": {"name": "Matching Straight Tailored Trousers", "fabric": "Water-Resistant Technical Linen", "silhouette": "Clean Flat Front Hem"},
                    "shoes": {"name": "Pointed Toe Leather Ankle Booties", "material": "Waterproof Treated Box Leather", "silhouette": "Low Architectural Kitten Heel"},
                    "jewellery": {
                        "necklace": {"name": "Layered Coin Charms on Non-Tarnish Steel", "metal": "PVD Gold / Platinum Coated"},
                        "earrings": {"name": "Double Interlocking Hoops", "metal": "Seamless Tubular Hoops"},
                        "lipstick_tint": {"name": "Nude Rosebud Cushion Lip Tint", "finish": "Hydrating Waterproof Satin Stain", "shade_desc": "Youthful natural lip enhancement"}
                    }
                }
            ]
        },
        "spring_autumn": {
            "male": [
                {
                    "upper": {"name": "Single-Breasted Hopsack Wool Blazer & Oxford Shirt", "fabric": "Open-Weave British Hopsack & Giza Cotton", "silhouette": "Tailored Notch Lapel Two-Button"},
                    "bottom": {"name": "Tailored Wool Flannel Dress Slacks", "fabric": "Super 130s Lightweight Flannel", "silhouette": "Single Pleat Clean Taper"},
                    "shoes": {"name": "Hand-Polished Leather Double Monk Straps", "material": "Antiqued Italian Calfskin", "silhouette": "Chiseled Toe Double Buckle"},
                    "jewellery": {
                        "rings": {"name": "Hammered Gold / Platinum Signet", "metal": "Satin 18k Metal"},
                        "earrings": {"name": "Micro Beveled Stud", "metal": "Titanium Setting"},
                        "watch": {"name": "Chronometer with Blue Steel Hands", "dial": "Enamel White Dial on Croc Strap"}
                    }
                },
                {
                    "upper": {"name": "Fine-Gauge Cashmere Knit under Sharp Wool Suit", "fabric": "Grade-A Cashmere & Worsted Wool", "silhouette": "Crewneck Layer under Suit"},
                    "bottom": {"name": "Matching Wool Suit Trousers", "fabric": "Virgin Wool Worsted Twill", "silhouette": "Sharp Creased Trousers"},
                    "shoes": {"name": "Wholecut Calfskin Oxfords", "material": "Single Cut Burnished Calf", "silhouette": "Seamless Formal Oxford"},
                    "jewellery": {
                        "rings": {"name": "Beveled Precious Metal Band", "metal": "Dual Finish Platinum / Gold"},
                        "earrings": {"name": "Clean Huggie Hoop", "metal": "Brushed Minimalist Hoop"},
                        "watch": {"name": "Heritage Automatic Horology", "dial": "Sunburst Champagne / Slate Dial"}
                    }
                },
                {
                    "upper": {"name": "Houndstooth Wool Blazer over Sea-Island Shirt", "fabric": "Scottish Lambswool & Sea-Island Cotton", "silhouette": "Subtle Micro-Check Structure"},
                    "bottom": {"name": "High-Waist Cavalry Twill Trousers", "fabric": "English Cavalry Twill", "silhouette": "Side Adjusters Gurkha Style"},
                    "shoes": {"name": "Burgundy Leather Penny Loafers", "material": "Cordovan-Style Gloss Calf", "silhouette": "Classic Penny Strap Silhouette"},
                    "jewellery": {
                        "rings": {"name": "Engraved Vintage Signet", "metal": "Antiqued Warm Alloy"},
                        "earrings": {"name": "Micro Square Stud", "metal": "Matte Dark Metal"},
                        "watch": {"name": "Fluted Bezel Horology with Jubilee Bracelet", "dial": "Olive / Silver Sunburst Dial"}
                    }
                },
                {
                    "upper": {"name": "Silk-Wool Blend Tuxedo Jacket for Formal Evenings", "fabric": "Silk & Worsted Wool Blend", "silhouette": "Satin Peak Lapel Evening Blazer"},
                    "bottom": {"name": "Tailored Tuxedo Pants with Silk Braid", "fabric": "Fine Wool Barathea", "silhouette": "Formal Midnight Trousers"},
                    "shoes": {"name": "Patent Leather Evening Slippers", "material": "Gloss Patent Leather", "silhouette": "Grosgrain Trim Velvet/Patent Slip-on"},
                    "jewellery": {
                        "rings": {"name": "Solid Gold / Platinum Heavy Signet", "metal": "Mirror-Polished Precious Metal"},
                        "earrings": {"name": "Brilliant-Cut Solitaire Stud", "metal": "Four-Prong Diamond Setting"},
                        "watch": {"name": "Ultra-Slim Black-Tie Horology", "dial": "Onyx Minimalist Dial"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Silk Satin Crepe Blouse & Tailored Wool Blazer", "fabric": "Heavy Silk Satin & Italian Wool", "silhouette": "Sculptural Tailored Peak Lapel"},
                    "bottom": {"name": "High-Rise Pleated Suiting Trousers", "fabric": "Fluid Worsted Wool Drape", "silhouette": "Wide-Leg Floor Skim"},
                    "shoes": {"name": "Pointed Suede Stiletto Pumps", "material": "Kid Suede with Leather Soles", "silhouette": "Timeless 75mm Pointed Heel"},
                    "jewellery": {
                        "necklace": {"name": "Sculptural Chunky Chain Choker", "metal": "18k Warm Gold or High-Shine Platinum"},
                        "earrings": {"name": "Molten Droplet Stud Earrings", "metal": "Textured Liquid Metal"},
                        "lipstick_tint": {"name": "Velvet Terracotta / Rose Executive Tint", "finish": "Hydrating Velvet Matte", "shade_desc": "Commanding and impeccably balanced with skin tone"}
                    }
                },
                {
                    "upper": {"name": "Double-Breasted Crepe Tuxedo Jacket", "fabric": "Italian Heavy Wool Crepe", "silhouette": "Satin Peak Lapel Hourglass"},
                    "bottom": {"name": "Matching Fluid Crepe Cigarette Trousers", "fabric": "Double Crepe Pressed Crease", "silhouette": "Ankle-Crop Sleek Silhouette"},
                    "shoes": {"name": "Patent Leather D'Orsay Pumps", "material": "High-Shine Mirror Patent Calf", "silhouette": "Arch Cutout Stiletto"},
                    "jewellery": {
                        "necklace": {"name": "Delicate Rivière Crystal Necklace", "metal": "Continuous Prong Setting"},
                        "earrings": {"name": "Cascading Crystal Drop Earrings", "metal": "Linear Sparkle Drops"},
                        "lipstick_tint": {"name": "Ruby / Spiced Wine Velvet Lip", "finish": "Rich Velvet Cushion Stain", "shade_desc": "High-impact glamorous depth"}
                    }
                },
                {
                    "upper": {"name": "Fine-Gauge Merino Rollneck under Wool Suiting", "fabric": "100% Merino Wool & Worsted Suiting", "silhouette": "High-Neck Layered Elegance"},
                    "bottom": {"name": "Matching Column Wool Trousers", "fabric": "Worsted Wool Stretch Weave", "silhouette": "Sharp Front Crease Column"},
                    "shoes": {"name": "Square-Toe Leather Block-Heel Pumps", "material": "Buttery Glove Leather", "silhouette": "Modern Architectural Heel"},
                    "jewellery": {
                        "necklace": {"name": "Liquid Snake Chain Collar", "metal": "High Luster Fluid Metal"},
                        "earrings": {"name": "Chunky Tubular C-Hoops", "metal": "Hollow Lightweight Metal"},
                        "lipstick_tint": {"name": "Warm Chestnut Nude Velvet", "finish": "Satin Longwear Cream", "shade_desc": "Sophisticated boardroom nude"}
                    }
                },
                {
                    "upper": {"name": "Silk Charmeuse Draped Wrap Blouse", "fabric": "Pure Silk Charmeuse Lustrous Weave", "silhouette": "Crossover Surplice Neckline"},
                    "bottom": {"name": "High-Waist Tailored Midi Pencil Skirt", "fabric": "Heavy Stretch Crepe", "silhouette": "Flattering Contour with Back Vent"},
                    "shoes": {"name": "Leather Slingback Kitten Heels", "material": "Fine Burnished Calfskin", "silhouette": "Pointed Toe Elegant Slingback"},
                    "jewellery": {
                        "necklace": {"name": "Baroque Pearl on Gold / Platinum Link", "metal": "Natural Irregular Pearl"},
                        "earrings": {"name": "Stacked Minimalist Baguette Studs", "metal": "Geometric Set Gemstones"},
                        "lipstick_tint": {"name": "Rosewood Petal Glaze Tint", "finish": "Luminous Serum Tint", "shade_desc": "Subtle dewy youthfulness with executive polish"}
                    }
                }
            ]
        }
    },
    "streetwear": {
        "summer": {
            "male": [
                {
                    "upper": {"name": "Heavyweight Boxy Drop-Shoulder Tee", "fabric": "280 GSM Combed Ring-Spun Cotton", "silhouette": "Oversized Streetwear Boxy"},
                    "bottom": {"name": "Relaxed Baggy Cargo Shorts", "fabric": "Washed Cotton Twill with Snap Pockets", "silhouette": "Below-the-Knee Baggy Cargo"},
                    "shoes": {"name": "Retro Suede Panel Chunky Sneakers", "material": "Suede, Mesh & Gum Rubber Sole", "silhouette": "Y2K Skate-Inspired Low-Top"},
                    "jewellery": {
                        "rings": {"name": "Chunky Curb Chain Ring", "metal": "Oxidized Silver or Distressed Brass"},
                        "earrings": {"name": "Dangling Safety-Pin Earring", "metal": "Industrial Stainless Steel"},
                        "watch": {"name": "Digital G-Shock / Retro Metal", "dial": "Electro-Luminescent Digital"}
                    }
                },
                {
                    "upper": {"name": "Mesh Basketball Jersey Layered over Tank", "fabric": "Perforated Air-Mesh Poly-Cotton", "silhouette": "Athletic Sleeveless Oversized"},
                    "bottom": {"name": "Wide-Leg Skater Denim Shorts", "fabric": "Heavy Washed 13oz Indigo Denim", "silhouette": "Baggy Raw-Edge Hem"},
                    "shoes": {"name": "High-Top Retro Leather Sneakers", "material": "Napa Leather with Color-Block Accents", "silhouette": "Padded Ankle Collar High-Top"},
                    "jewellery": {
                        "rings": {"name": "Engraved Gothic Band", "metal": "Distressed Antique Alloy"},
                        "earrings": {"name": "Small Black Stud Huggie", "metal": "Anodized Black Metal"},
                        "watch": {"name": "Chunky Resin Diver", "dial": "Color-Matched Bezel"}
                    }
                },
                {
                    "upper": {"name": "Vintage-Wash Acid Drop Graphic Tee", "fabric": "Single Jersey Pigment-Dyed Cotton", "silhouette": "Drop Shoulder Vintage Fade"},
                    "bottom": {"name": "Nylon Parachute Relaxed Pants", "fabric": "Crinkle Ultralight Tech Nylon", "silhouette": "Bungee Ankle Toggle Baggy"},
                    "shoes": {"name": "Tech Runner Trail Sneakers", "material": "Ripstop & Vibram Megagrip", "silhouette": "Chunky Lug Trail Silhouette"},
                    "jewellery": {
                        "rings": {"name": "Spinning Mechanical Ring", "metal": "High-Precision Steel"},
                        "earrings": {"name": "Barbed Wire Motif Huggie", "metal": "Polished Silver / Gold Tone"},
                        "watch": {"name": "Minimalist Transparent Skeleton Watch", "dial": "Exposed Mechanical Movement"}
                    }
                },
                {
                    "upper": {"name": "Camp-Collar Rayon Shirt with Abstract Texture", "fabric": "100% Breathable Viscose Rayon", "silhouette": "Relaxed Flowy Open Collar"},
                    "bottom": {"name": "Wide-Leg Raw Pleated Cotton Pants", "fabric": "Heavy Canvas Cotton Twill", "silhouette": "Roomy Wide Skate Fit"},
                    "shoes": {"name": "Suede Mule Slides with Cork Bed", "material": "Thick Suede with Buckle Detail", "silhouette": "Slip-On Street Mule"},
                    "jewellery": {
                        "rings": {"name": "Stacked Dual Rings", "metal": "Contrast Polished and Matte"},
                        "earrings": {"name": "Single Cross Drop Earring", "metal": "Subtle Gothic Drop"},
                        "watch": {"name": "Industrial Matte Horology on Nylon", "dial": "Monochrome Minimalist Face"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Cropped Baby Tee with Contrast Stitch", "fabric": "Organic Cotton Baby Rib", "silhouette": "Fitted Y2K Crop Cut"},
                    "bottom": {"name": "Ultra Wide-Leg Parachute Pants", "fabric": "Crinkle Lightweight Tech Nylon", "silhouette": "Low-Rise Bungee Drawstring"},
                    "shoes": {"name": "Chunky Platform Retro Sneakers", "material": "Tumbled Leather with Platform Midsole", "silhouette": "Platform Skate Sneaker"},
                    "jewellery": {
                        "necklace": {"name": "Chunky Star-Pendant Ball Chain", "metal": "Polished Stainless Steel"},
                        "earrings": {"name": "Thick Hollow Chunky Hoops", "metal": "18k Warm Gold or Silver Plated"},
                        "lipstick_tint": {"name": "Y2K Glossy Brown / Coral Lip Glaze", "finish": "Ultra-Shine Mirror Plumping Tint", "shade_desc": "Glossy high-shine statement lip"}
                    }
                },
                {
                    "upper": {"name": "Oversized Graphic Mesh Racer Tank", "fabric": "Air-Knit Open Mesh", "silhouette": "Boyfriend Slouchy Racerback"},
                    "bottom": {"name": "Baggy Carpenter Denim Shorts", "fabric": "Light-Wash Stiff 100% Cotton Denim", "silhouette": "Low-Slung Loose Cargo"},
                    "shoes": {"name": "Vintage Low-Top Skate Shoes", "material": "Suede and Canvas Upper", "silhouette": "Vulcanized Gum Sole"},
                    "jewellery": {
                        "necklace": {"name": "Layered Micro Pearls with Chain", "metal": "Freshwater Pearls on Industrial Links"},
                        "earrings": {"name": "Safety Pin & Stud Set", "metal": "Asymmetrical Ear Curation"},
                        "lipstick_tint": {"name": "Vibrant Popsicle Stained Tint", "finish": "Longwear Water Stain", "shade_desc": "Youthful energetic stained flush"}
                    }
                },
                {
                    "upper": {"name": "Ribbed Halter Tube Top with Shrug", "fabric": "High-Stretch Seamless Rib", "silhouette": "Bandeau with Bolero Sleeves"},
                    "bottom": {"name": "High-Waist Wide-Leg Pleated Chinos", "fabric": "Heavy Washed Chino Twill", "silhouette": "Oversized Puddle Hem"},
                    "shoes": {"name": "Chunky Dad Runner Sneakers", "material": "Mesh & Metallic Silver Overlays", "silhouette": "Sculpted Chunky Midsole"},
                    "jewellery": {
                        "necklace": {"name": "Liquid Metal Snake Choker", "metal": "Chunky Flat Snake Chain"},
                        "earrings": {"name": "Bold Teardrop Chunky Studs", "metal": "Viral Molten Droplets"},
                        "lipstick_tint": {"name": "Velvet Nude Brown Lip Tint", "finish": "Soft-Focus Blur Matte", "shade_desc": "Street-style modern 90s contour nude"}
                    }
                },
                {
                    "upper": {"name": "Oversized Bowling Shirt with Contrast Trim", "fabric": "Satin-Finish Tencel Poplin", "silhouette": "Relaxed Boxy Open Placket"},
                    "bottom": {"name": "Micro Pleated Skort in Streetwear Twill", "fabric": "Structured Poly-Viscose Crepe", "silhouette": "Tennis Skort with Built-in Shorts"},
                    "shoes": {"name": "High-Top Canvas Sneakers with Lug Sole", "material": "Heavyweight Cotton Canvas", "silhouette": "Platform Lug Sole High-Top"},
                    "jewellery": {
                        "necklace": {"name": "Gothic Letter Initial Pendant", "metal": "Heavy Link with Old English Initial"},
                        "earrings": {"name": "Spike Huggie Drop Earrings", "metal": "Edgy Micro Spike Charms"},
                        "lipstick_tint": {"name": "Dewy Cherry Tint Oil", "finish": "Plumping Oil Glow", "shade_desc": "Glassy mirror shine cherry / coral"}
                    }
                }
            ]
        },
        "winter": {
            "male": [
                {
                    "upper": {"name": "Heavyweight 450 GSM Fleece Hoodie & Puffer", "fabric": "100% French Terry Cotton & Ripstop", "silhouette": "Drop-Shoulder Boxy Hoodie & Cropped Puffer"},
                    "bottom": {"name": "Baggy Double-Knee Carpenter Pants", "fabric": "12oz Duck Canvas Cotton", "silhouette": "Relaxed Skate Carpenter Fit"},
                    "shoes": {"name": "Gore-Tex Winter High-Top Sneakers", "material": "Waterproof Leather & Cordura", "silhouette": "Weatherproof Chunky High-Top"},
                    "jewellery": {
                        "rings": {"name": "Chunky Signet with Compass Motif", "metal": "Brushed Steel / Antique Gold"},
                        "earrings": {"name": "Single Spike Earring", "metal": "Blackened Stainless Steel"},
                        "watch": {"name": "Tactical Multi-Sensor Digital", "dial": "Negative Display on Resin"}
                    }
                },
                {
                    "upper": {"name": "Sherpa Fleece Zip Jacket over Thermal", "fabric": "Deep-Pile Japanese Sherpa Fleece", "silhouette": "Relaxed Stand-Collar Zip"},
                    "bottom": {"name": "Wide-Leg Fleece Sweatpants", "fabric": "Heavy Brushed Loopback Cotton", "silhouette": "Cinched Bungee Ankle"},
                    "shoes": {"name": "Lug-Sole Suede Winter Mules", "material": "Treated Water-Repellent Suede", "silhouette": "Padded Slip-On Street Shoe"},
                    "jewellery": {
                        "rings": {"name": "Industrial Nut & Bolt Band", "metal": "Hardware Inspired Ring"},
                        "earrings": {"name": "Micro Geometric Stud", "metal": "Titanium Setting"},
                        "watch": {"name": "Matte Monochrome Watch", "dial": "All-Black or All-Gold Dial"}
                    }
                },
                {
                    "upper": {"name": "Varsity Bomber Jacket with Leather Sleeves", "fabric": "Melton Wool Body & Cowhide Leather", "silhouette": "Boxy Cropped Varsity"},
                    "bottom": {"name": "Relaxed Vintage Wash Jeans", "fabric": "14oz Heavy Rigid Denim", "silhouette": "Loose Straight Leg"},
                    "shoes": {"name": "Classic Retro Basketball Mid-Tops", "material": "Full-Grain Leather with Suede Accents", "silhouette": "Mid-Top Padded Tongue"},
                    "jewellery": {
                        "rings": {"name": "Heavy Curb Chain Ring", "metal": "Heavyweight Solid Metal"},
                        "earrings": {"name": "Minimal Huggie", "metal": "Subtle Gold / Silver Accent"},
                        "watch": {"name": "Gold Chrono on Steel Bracelet", "dial": "Sunburst Dial"}
                    }
                },
                {
                    "upper": {"name": "Down Puffer Vest over Mohair Knit Sweater", "fabric": "Brushed Kid Mohair & Goose Down", "silhouette": "Oversized Hairy Knit Texture"},
                    "bottom": {"name": "Heavy Corduroy Baggy Pants", "fabric": "Wide 6-Wale Cotton Corduroy", "silhouette": "Relaxed Puddle Hem"},
                    "shoes": {"name": "Chunky Lug Derby Shoes", "material": "Polished Spazzolato Calf", "silhouette": "Platform Lug Welt"},
                    "jewellery": {
                        "rings": {"name": "Two-Finger Statement Ring", "metal": "Cast Architectural Ring"},
                        "earrings": {"name": "Black Obsidian Stud", "metal": "Matte Finish Setting"},
                        "watch": {"name": "Automatic with Skeleton Back", "dial": "Industrial Dial on Heavy Steel"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Cropped Down Puffer Jacket & Hoodie", "fabric": "Matte Nylon Shell with 700 Fill Down", "silhouette": "Cropped Bungee Cinched Puffer"},
                    "bottom": {"name": "High-Waist Wide-Leg Fleece Sweats", "fabric": "420 GSM Ultra-Soft Brushed Fleece", "silhouette": "Oversized Balloon Leg"},
                    "shoes": {"name": "Chunky Platform Suede Booties", "material": "Treated Water-Repellent Suede", "silhouette": "Slip-on Platform Winter Bootie"},
                    "jewellery": {
                        "necklace": {"name": "Chunky Industrial Link Chain", "metal": "Oversized Links with Lobster Clasp"},
                        "earrings": {"name": "Bold Tubing Chunky Hoops", "metal": "Hollow 18k Plated or Silver"},
                        "lipstick_tint": {"name": "Deep Plum Velvet Matte Stain", "finish": "Longwear Velvet Cloud", "shade_desc": "Edgy 90s streetwear statement plum"}
                    }
                },
                {
                    "upper": {"name": "Oversized Faux-Fur Moto Jacket", "fabric": "Plush Faux Shearling & Vegan Leather", "silhouette": "Boxy Asymmetrical Zip Moto"},
                    "bottom": {"name": "Baggy Straight-Leg Washed Denim", "fabric": "Heavyweight 100% Cotton Denim", "silhouette": "Mid-Rise Relaxed Slouch"},
                    "shoes": {"name": "High-Platform Leather Combat Boots", "material": "Full-Grain Waxed Leather", "silhouette": "Lace-Up Lug Platform"},
                    "jewellery": {
                        "necklace": {"name": "Padlock Charm on Paperclip Chain", "metal": "High-Polish Metal Padlock"},
                        "earrings": {"name": "Spike Drop Earrings", "metal": "Punk-Inspired Drop Charms"},
                        "lipstick_tint": {"name": "Espresso Nude Velvet Lip Ink", "finish": "Transfer-Proof Velvet Matte", "shade_desc": "Moody dark chocolate nude"}
                    }
                },
                {
                    "upper": {"name": "Distressed Mohair Knit Sweater", "fabric": "Open-Weave Brushed Alpaca & Mohair", "silhouette": "Slouchy One-Shoulder Drop"},
                    "bottom": {"name": "Cargo Maxi Skirt with Toggle Pockets", "fabric": "Crisp Technical Parachute Cotton", "silhouette": "High-Waist Column with Back Slit"},
                    "shoes": {"name": "Chunky Square-Toe Platform Boots", "material": "Gloss Leather with Stretch Shaft", "silhouette": "Sock Boot on Chunky Lug"},
                    "jewellery": {
                        "necklace": {"name": "Multi-Strand Ball & Box Chains", "metal": "Layered Urban Hardware"},
                        "earrings": {"name": "Safety Pin Hoops", "metal": "Edgy Wire Piercings"},
                        "lipstick_tint": {"name": "Velvet Spiced Berry Tint", "finish": "Hydrating Velvet Strobe", "shade_desc": "Vampy rich berry flush"}
                    }
                },
                {
                    "upper": {"name": "Fleece Half-Zip with Contrast Nylon Pocket", "fabric": "Heavy Sherpa Fleece with Tech Paneling", "silhouette": "Relaxed Pullover Half-Zip"},
                    "bottom": {"name": "Baggy Cargo Pants with Straps", "fabric": "Heavy Cotton Ripstop", "silhouette": "Multi-Pocket Streetwear Silhouette"},
                    "shoes": {"name": "Retro Trail Chunky Sneakers", "material": "Mesh, Cordura & Vibram Sole", "silhouette": "Y2K Gorpcore Sneaker"},
                    "jewellery": {
                        "necklace": {"name": "Heavy Cuban Link Choker", "metal": "12mm Diamond-Cut Curb"},
                        "earrings": {"name": "Chunky Molten Studs", "metal": "Reflective Liquid Metal"},
                        "lipstick_tint": {"name": "Toasted Caramel Velvet Lip", "finish": "Velvet Cushion Stain", "shade_desc": "Warm caramel spiced nude"}
                    }
                }
            ]
        },
        "monsoon": {
            "male": [
                {
                    "upper": {"name": "Hooded Technical Windbreaker", "fabric": "Three-Layer Waterproof DWR Nylon", "silhouette": "Boxy Raglan Zip Anorak"},
                    "bottom": {"name": "Tapered Water-Repellent Cargo Pants", "fabric": "Matte Stretch Ripstop", "silhouette": "Articulated Knee Cargo"},
                    "shoes": {"name": "Gore-Tex Trail Runner Sneakers", "material": "Seamless Synthetic & Megagrip", "silhouette": "All-Weather Technical Runner"},
                    "jewellery": {
                        "rings": {"name": "Black Titanium Ring", "metal": "Scratch-Proof Matte Black"},
                        "earrings": {"name": "Micro Anodized Stud", "metal": "Industrial Black Titanium"},
                        "watch": {"name": "All-Weather G-Shock on Resin", "dial": "Solar Digital Display"}
                    }
                },
                {
                    "upper": {"name": "Oversized Heavy Tee with Water-Repellent Vest", "fabric": "Heavy Cotton & DWR Tech Canvas", "silhouette": "Multi-Pocket Tactical Vest Layer"},
                    "bottom": {"name": "Baggy Nylon Track Pants", "fabric": "Crinkle Water-Shedding Taslan Nylon", "silhouette": "Relaxed Elastic Cuffed Hem"},
                    "shoes": {"name": "Waterproof High-Top Street Boots", "material": "Water-Sealed Leather & Rubber Lug", "silhouette": "Lugged Platform Sneaker Boot"},
                    "jewellery": {
                        "rings": {"name": "Hammered Tungsten Band", "metal": "High-Durability Heavyweight Alloy"},
                        "earrings": {"name": "Small Hoop with Bar Charm", "metal": "Non-Tarnish Stainless Steel"},
                        "watch": {"name": "Tactical Field Watch with Olive Strap", "dial": "Matte Military Dial"}
                    }
                },
                {
                    "upper": {"name": "Popover Shell Anorak over Thermal", "fabric": "Breathable Rainproof Micro-Ripstop", "silhouette": "Kangaroo Pocket Half-Zip"},
                    "bottom": {"name": "Quick-Dry Tech Parachute Pants", "fabric": "Ultralight Moisture-Wicking Nylon", "silhouette": "Wide Leg Bungee Drawstring"},
                    "shoes": {"name": "Slip-on Waterproof Tech Mules", "material": "Molded EVA with Rubber Traction", "silhouette": "Ergonomic Street Slip-on"},
                    "jewellery": {
                        "rings": {"name": "Etched Urban Band", "metal": "Laser-Cut Industrial Steel"},
                        "earrings": {"name": "Minimalist Ball Stud", "metal": "Surgical Steel"},
                        "watch": {"name": "Aqua-Diver on Silicone Strap", "dial": "Luminescent Dial"}
                    }
                },
                {
                    "upper": {"name": "Short-Sleeve Utility Overshirt over Compression Tee", "fabric": "DWR Coated Poplin & Quick-Dry Spandex", "silhouette": "Snap Button Urban Utility"},
                    "bottom": {"name": "Water-Repellent Baggy Denim Jeans", "fabric": "Fluorocarbon-Free DWR Treated Denim", "silhouette": "Loose Fit Straight Cut"},
                    "shoes": {"name": "Weatherproof Leather Low Sneakers", "material": "Water-Sealed Tumbled Leather", "silhouette": "Rubber Toe-Cap Street Sneaker"},
                    "jewellery": {
                        "rings": {"name": "Dual-Finish Signet", "metal": "Brushed and Polished Contrast"},
                        "earrings": {"name": "Low-Profile Huggie", "metal": "Black PVD Coated Metal"},
                        "watch": {"name": "Digital Chrono on Textured Strap", "dial": "High-Contrast Backlit Screen"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Cropped Technical Rain Jacket", "fabric": "Matte 2.5-Layer Waterproof Fabric", "silhouette": "High Funnel Neck Bungee Cinch"},
                    "bottom": {"name": "High-Waist Parachute Cargo Pants", "fabric": "Quick-Dry Ripstop Nylon", "silhouette": "Baggy Utility with Bungee Ankle"},
                    "shoes": {"name": "Platform Waterproof Lug Chelsea Boots", "material": "Sealed Rubberized Leather", "silhouette": "Chunky Track Sole"},
                    "jewellery": {
                        "necklace": {"name": "Stainless Steel Industrial Chain", "metal": "Non-Tarnish High-Shine Steel"},
                        "earrings": {"name": "Chunky Waterproof Tube Hoops", "metal": "PVD Coated Gold / Silver"},
                        "lipstick_tint": {"name": "Transfer-Proof Lip Ink Stain", "finish": "Water-Locked Matte Tint", "shade_desc": "Longwearing vibrant berry or peach"}
                    }
                },
                {
                    "upper": {"name": "Oversized Water-Repellent Vest over Baby Tee", "fabric": "Quilted DWR Poplin & Stretch Cotton", "silhouette": "Zip Utility Layering"},
                    "bottom": {"name": "Coated Baggy Cargo Skirt", "fabric": "Wax-Coated Water-Repellent Twill", "silhouette": "Midi Cargo with High Front Slit"},
                    "shoes": {"name": "Waterproof Chunky Trail Sneakers", "material": "Gore-Tex Lined Breathable Mesh", "silhouette": "Chunky Grip Street Runner"},
                    "jewellery": {
                        "necklace": {"name": "Lock Charm on Box Link", "metal": "Waterproof Stainless Alloy"},
                        "earrings": {"name": "Micro Spikes Huggies", "metal": "Tarnish-Resistant Titanium"},
                        "lipstick_tint": {"name": "Hydra-Gel Stained Lip Oil", "finish": "Humidity-Resistant Gel Tint", "shade_desc": "Juicy non-sticky all-day stain"}
                    }
                },
                {
                    "upper": {"name": "Transparent Hooded Rain Pullover over Sports Bra", "fabric": "Semi-Sheer Matte TPU Weather Fabric", "silhouette": "Oversized Drawstring Smock"},
                    "bottom": {"name": "High-Waist Biker Shorts with Pocket", "fabric": "Quick-Dry Compression Spandex", "silhouette": "Mid-Thigh Sleek Fit"},
                    "shoes": {"name": "Platform Rain Duck Boots", "material": "Vulcanized Rubber & Neoprene", "silhouette": "Ankle Duck Boot Streetwear"},
                    "jewellery": {
                        "necklace": {"name": "Heavy Link Toggle Collar", "metal": "Water-Safe Polished Link"},
                        "earrings": {"name": "Molten Droplet Studs", "metal": "Seamless Metal Droplet"},
                        "lipstick_tint": {"name": "Velvet Rosebud Water Stain", "finish": "Weightless Velvet Veil", "shade_desc": "Soft rose petal hue that defies humidity"}
                    }
                },
                {
                    "upper": {"name": "Cropped Windbreaker Jacket with Hood", "fabric": "Ultralight Water-Shedding Poly", "silhouette": "Elastic Hem Cropped Fit"},
                    "bottom": {"name": "Wide-Leg Water-Resistant Track Pants", "fabric": "Matte Lightweight Nylon", "silhouette": "Side Stripe Loose Flow"},
                    "shoes": {"name": "Lug-Sole Leather Street Derby Shoes", "material": "Water-Sealed Patent Leather", "silhouette": "Chunky Platform Derby"},
                    "jewellery": {
                        "necklace": {"name": "Layered Snake & Cable Chains", "metal": "Tarnish-Proof PVD Gold"},
                        "earrings": {"name": "Chunky Oval Link Earrings", "metal": "Industrial Oval Drops"},
                        "lipstick_tint": {"name": "Terracotta Tint Lip Serum", "finish": "Longwear Satin Gel", "shade_desc": "Warm terracotta / berry rain-proof glow"}
                    }
                }
            ]
        },
        "spring_autumn": {
            "male": [
                {
                    "upper": {"name": "Cropped Vintage Leather Moto Jacket & Tee", "fabric": "Supple Lambskin & Heavy Ring-Spun Cotton", "silhouette": "Boxy Asymmetrical Zip Jacket"},
                    "bottom": {"name": "Relaxed Straight-Leg Raw Selvedge Denim", "fabric": "13.5oz Japanese Selvedge Twill", "silhouette": "Slight Baggy Straight Cut"},
                    "shoes": {"name": "Retro Suede Panel Low-Top Sneakers", "material": "Italian Suede & Leather Overlays", "silhouette": "Y2K Minimal Skate Sneaker"},
                    "jewellery": {
                        "rings": {"name": "Signet with Embossed Coin", "metal": "Warm Brass or Antiqued Silver"},
                        "earrings": {"name": "Minimalist Huggie Hoop", "metal": "Brushed Metal Stud"},
                        "watch": {"name": "Vintage Chrono on Leather", "dial": "Aged Patina Dial"}
                    }
                },
                {
                    "upper": {"name": "Oversized Flannel Plaid Overshirt & Thermal", "fabric": "Heavy Brushed Cotton Flannel (320 GSM)", "silhouette": "Drop Shoulder Double Pocket"},
                    "bottom": {"name": "Baggy Double-Knee Work Pants", "fabric": "Heavy Duck Canvas", "silhouette": "Loose Skate Fit"},
                    "shoes": {"name": "Handmade Suede Chelsea Boots with Crepe Sole", "material": "Snuff Calf Suede with Natural Crepe", "silhouette": "Casual Soft-Toe Chelsea"},
                    "jewellery": {
                        "rings": {"name": "Chunky Beveled Band", "metal": "Satin Precision Metal"},
                        "earrings": {"name": "Small Stud with Semiprecious Stone", "metal": "Tiger Eye / Onyx Inset"},
                        "watch": {"name": "Field Horology on Olive Canvas", "dial": "High-Visibility Numerals"}
                    }
                },
                {
                    "upper": {"name": "Half-Zip Fleece Pullover with Contrast Collar", "fabric": "Mid-Weight Polar Fleece & Taslan", "silhouette": "Retro 90s Color-Block Pullover"},
                    "bottom": {"name": "Wide-Leg Corduroy Skate Pants", "fabric": "8-Wale Rich Cotton Corduroy", "silhouette": "Roomy Straight Cut"},
                    "shoes": {"name": "High-Top Retro Court Sneakers", "material": "Pebbled Leather with Suede Accents", "silhouette": "Padded Collar Heritage Sneaker"},
                    "jewellery": {
                        "rings": {"name": "Dual-Tone Stacked Rings", "metal": "Contrast Polished and Matte"},
                        "earrings": {"name": "Micro Drop Cross Earring", "metal": "Clean Wire Charm"},
                        "watch": {"name": "Chronometer with Leather Strap", "dial": "Dark Textured Dial"}
                    }
                },
                {
                    "upper": {"name": "Bomber Jacket over Graphic Sweatshirt", "fabric": "Heavy Satin Nylon & French Terry", "silhouette": "Classic MA-1 Bomber Fit"},
                    "bottom": {"name": "Tapered Cargo Pants with Snap Hem", "fabric": "Washed Cotton Twill", "silhouette": "Articulated Tapered Leg"},
                    "shoes": {"name": "Suede Runner Sneakers with Gum Sole", "material": "Perforated Suede and Rubber", "silhouette": "Heritage Retro Runner"},
                    "jewellery": {
                        "rings": {"name": "Textured Band Ring", "metal": "Hammered Finish Alloy"},
                        "earrings": {"name": "Low-Profile Titanium Stud", "metal": "Minimal Flush Setting"},
                        "watch": {"name": "Digital Retro Gold/Steel Watch", "dial": "Classic Vintage Display"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Oversized Distressed Leather Bomber over Crop Tank", "fabric": "Washed Worn-In Leather & Stretch Modal", "silhouette": "Oversized 90s Bomber Fit"},
                    "bottom": {"name": "Low-Rise Baggy Cargo Jeans", "fabric": "12oz Washed Cotton Denim", "silhouette": "Floor-Length Baggy Cargo"},
                    "shoes": {"name": "Platform Suede Skate Sneakers", "material": "Brushed Suede with Gum Rubber Sole", "silhouette": "Chunky Platform Skate"},
                    "jewellery": {
                        "necklace": {"name": "Chunky Multi-Chain Collar with Heart Charm", "metal": "Layered Hardware Links"},
                        "earrings": {"name": "Thick Hollow Gold / Silver Hoops", "metal": "18k Warm Gold or Silver Plated"},
                        "lipstick_tint": {"name": "Warm Chestnut Velvet Lip Stain", "finish": "Soft Velvet Matte", "shade_desc": "Iconic 90s street-style chestnut flush"}
                    }
                },
                {
                    "upper": {"name": "Cropped Fuzzy Knit Cardigan as Top", "fabric": "Brushed Alpaca Wool Blend", "silhouette": "Deep V-Neck Ribbed Hem"},
                    "bottom": {"name": "High-Waist Wide-Leg Pleated Slacks", "fabric": "Heavyweight Drape Viscose Crepe", "silhouette": "Floor-Puddle Wide Cut"},
                    "shoes": {"name": "Pointed-Toe Knee-High Leather Boots", "material": "Full-Grain Italian Calf", "silhouette": "Mid Block Heel Street Boot"},
                    "jewellery": {
                        "necklace": {"name": "Molten Coin on Long Chain", "metal": "Textured Heavy Cast Coin"},
                        "earrings": {"name": "Chunky Teardrop Huggies", "metal": "Smooth Mirror Drops"},
                        "lipstick_tint": {"name": "Terracotta Sunset Plump Tint", "finish": "Hydrating Lip Serum Strobe", "shade_desc": "Warm sun-drenched earth glow"}
                    }
                },
                {
                    "upper": {"name": "Boxy Cropped Trench over Graphic Tee", "fabric": "Heavy Cotton Twill & Ring-Spun Jersey", "silhouette": "Storm Flap Cropped Trench"},
                    "bottom": {"name": "Denim Maxi Skirt with Front Slit", "fabric": "Non-Stretch 100% Cotton Denim", "silhouette": "High-Rise A-Line Column"},
                    "shoes": {"name": "Chunky Platform Derby Shoes", "material": "Polished Spazzolato Box Leather", "silhouette": "Platform Lug Sole Derby"},
                    "jewellery": {
                        "necklace": {"name": "Herringbone Liquid Metal Choker", "metal": "Flexible High Luster Chain"},
                        "earrings": {"name": "Safety Pin Drop Earrings", "metal": "Punk Minimalist Wire"},
                        "lipstick_tint": {"name": "Berry Wine Satin Lip Strobe", "finish": "Weightless Stained Finish", "shade_desc": "Luminous berry tint with effortless edge"}
                    }
                },
                {
                    "upper": {"name": "Oversized Varsity Knit with V-Neck", "fabric": "100% Merino Wool Chunky Knit", "silhouette": "Preppy Oversized Drop Shoulder"},
                    "bottom": {"name": "Wide-Leg Parachute Pants", "fabric": "Crisp Light Cotton Poplin", "silhouette": "Bungee Hem Slouchy Fit"},
                    "shoes": {"name": "Retro Leather High-Top Court Shoes", "material": "Napa Leather with Color Pops", "silhouette": "Classic Padded High-Top"},
                    "jewellery": {
                        "necklace": {"name": "Double Layered Ball Chain", "metal": "Industrial Stainless Steel"},
                        "earrings": {"name": "Bold Oval Chunky Studs", "metal": "Cast Smooth Metal"},
                        "lipstick_tint": {"name": "Nude Caramel Lip Oil Tint", "finish": "Nourishing High-Shine Glaze", "shade_desc": "Plump caramel glaze harmonized with skin"}
                    }
                }
            ]
        }
    },
    "ethnic": {
        "summer": {
            "male": [
                {
                    "upper": {"name": "Chanderi Silk-Cotton Kurta with Mandarin Collar", "fabric": "Handwoven Chanderi Silk & Cotton", "silhouette": "Straight Knee-Length Kurta"},
                    "bottom": {"name": "Crisp Cotton Churidar / Pajama Trousers", "fabric": "Breathable Lightweight Cotton", "silhouette": "Tailored Slim Churidar"},
                    "shoes": {"name": "Hand-Embroidered Leather Mojaris / Juttis", "material": "Soft Camel Leather with Thread Work", "silhouette": "Traditional Pointed Toe Mojari"},
                    "jewellery": {
                        "rings": {"name": "Engraved Navratna / Gemstone Gold Ring", "metal": "18k Warm Gold with Stone Inset"},
                        "earrings": {"name": "Minimalist Gold Huggie Stud", "metal": "Pure Gold Single Stud"},
                        "watch": {"name": "Horology with Gold Dial on Leather", "dial": "Classic Champagne Dial"}
                    }
                },
                {
                    "upper": {"name": "Short Linen-Cotton Kurta Shirt", "fabric": "Pure Indian Flax Linen", "silhouette": "Banded Collar Modern Kurta"},
                    "bottom": {"name": "Tailored Dhoti Pants / Pleated Slacks", "fabric": "Fine Cotton Cambric", "silhouette": "Pre-Stitched Draped Dhoti"},
                    "shoes": {"name": "Kolhapuri Leather Sandals", "material": "Handcrafted Veg-Tanned Leather", "silhouette": "Braided Toe-Loop Kolhapuri"},
                    "jewellery": {
                        "rings": {"name": "Hammered Gold Signet", "metal": "Solid Gold Ring"},
                        "earrings": {"name": "Micro Beveled Stud", "metal": "Surgical Titanium"},
                        "watch": {"name": "Chronometer with Tan Leather Strap", "dial": "Clean Textured Face"}
                    }
                },
                {
                    "upper": {"name": "Lucknowi Chikankari Embroidered Kurta", "fabric": "Pure Mulmul Cotton with Intricate Shadow Work", "silhouette": "Relaxed Flared Hem Kurta"},
                    "bottom": {"name": "Straight Linen Aligarh Pajama", "fabric": "Lightweight Linen Blend", "silhouette": "Clean Straight Leg Cut"},
                    "shoes": {"name": "Crust Leather Velvet-Lined Juttis", "material": "Hand-Dyed Soft Calfskin", "silhouette": "Cushioned Traditional Jutti"},
                    "jewellery": {
                        "rings": {"name": "Filigree Work Signet Ring", "metal": "Traditional Gold Filigree"},
                        "earrings": {"name": "Subtle Gold Stud", "metal": "22k Warm Yellow Gold"},
                        "watch": {"name": "Vintage Gold Dress Watch", "dial": "Ivory Dial with Roman Numerals"}
                    }
                },
                {
                    "upper": {"name": "Bandhgala Nehru Jacket over Linen Kurta", "fabric": "Hand-Spun Matka Silk & Khadi", "silhouette": "Structured Sleeveless Bandhgala"},
                    "bottom": {"name": "Slim Tailored Cotton Trousers", "fabric": "High-Twist Fine Cotton Twill", "silhouette": "Clean Flat-Front Hem"},
                    "shoes": {"name": "Hand-Burnished Leather Monk Straps", "material": "Italian Calfskin with Brass Buckle", "silhouette": "Cross-Cultural Elegant Loafer"},
                    "jewellery": {
                        "rings": {"name": "Carved Jade / Carnelian Ring", "metal": "Precious Metal with Semi-Precious Gem"},
                        "earrings": {"name": "Minimalist Huggie", "metal": "Low-Profile Polished Metal"},
                        "watch": {"name": "Horology with Gold-Tone Mesh", "dial": "Sunburst Dial"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Chanderi Silk Anarkali / Kurti with Zari Border", "fabric": "Handloom Chanderi Silk with Real Zari", "silhouette": "Flared Flattering Kalidar Kurti"},
                    "bottom": {"name": "Straight Silk Trousers with Scalloped Hem", "fabric": "Fine Mashru Silk", "silhouette": "Cropped Ankle Hem with Zari Detail"},
                    "shoes": {"name": "Zari-Embroidered Padded Juttis", "material": "Soft Leather with Silk Embroidery", "silhouette": "Padded Comfort Sole Jutti"},
                    "jewellery": {
                        "necklace": {"name": "Polki / Kundan Choker with Pearls", "metal": "22k Gold Foil Setting with Emerald / Ruby beads"},
                        "earrings": {"name": "Chandbali Drop Earrings", "metal": "Intricate Crescent Filigree with Seed Pearls"},
                        "lipstick_tint": {"name": "Warm Terracotta Sindoori Tint", "finish": "Hydrating Velvet Stained Cream", "shade_desc": "Traditional auspicious terracotta rose"}
                    }
                },
                {
                    "upper": {"name": "Organza Floral Printed Saree / Blouse", "fabric": "Pure Crisp Silk Organza with Hand-Painted Motifs", "silhouette": "Sweetheart Neckline Padded Blouse"},
                    "bottom": {"name": "Flowing Organza Saree Draped Skirt", "fabric": "Matching Sheer Organza Silk", "silhouette": "Fluid Classical Saree Pleats"},
                    "shoes": {"name": "Strappy Metallic Heeled Kolhapuris", "material": "Metallic Leather Straps with Block Heel", "silhouette": "Contemporary Ethnic Heeled Sandal"},
                    "jewellery": {
                        "necklace": {"name": "Layered Temple Jewelry Choker", "metal": "Matte Antique Gold with Carved Goddess Motifs"},
                        "earrings": {"name": "Classic Jhumkas with Bell Drops", "metal": "Tiered Jhumka with Pearl Hangings"},
                        "lipstick_tint": {"name": "Petal Rose Dewy Lip Tint", "finish": "Luminous Serum Stained Lip", "shade_desc": "Youthful blooming rose glow"}
                    }
                },
                {
                    "upper": {"name": "Chikankari Georgette Kurta with Mukaish Work", "fabric": "Pure Silk Georgette with Metallic Kamdani", "silhouette": "Graceful Straight Cut A-Line"},
                    "bottom": {"name": "Flared Georgette Sharara Pants", "fabric": "Triple-Tier Pleated Georgette", "silhouette": "Dramatic Flowing Sharara Leg"},
                    "shoes": {"name": "Embellished Silk Kitten-Heel Mules", "material": "Raw Silk with Dabka & Zardozi Work", "silhouette": "Pointed Toe Ethnic Mule"},
                    "jewellery": {
                        "necklace": {"name": "Navratna Choker with Tourmaline Beads", "metal": "Nine-Gem Astrological Setting in Gold"},
                        "earrings": {"name": "Passa-Inspired Drop Earrings", "metal": "Cascading Fine Seed Pearls"},
                        "lipstick_tint": {"name": "Warm Peach Nude Velvet", "finish": "Soft-Focus Blur Matte", "shade_desc": "Modern fresh Indian ethnic nude"}
                    }
                },
                {
                    "upper": {"name": "Raw Silk Peplum Top with Zardozi Work", "fabric": "Handwoven Banarasi Katan Silk", "silhouette": "Structured Peplum with Boat Neck"},
                    "bottom": {"name": "Brocade Cigar Pants with Gold Weave", "fabric": "Pure Zari Brocade Silk", "silhouette": "Tailored High-Waist Cigar Ankle"},
                    "shoes": {"name": "Criss-Cross Metallic Leather Flats", "material": "Rose Gold / Antique Gold Leather", "silhouette": "Comfort Flat with Ankle Tie"},
                    "jewellery": {
                        "necklace": {"name": "Meenakari Enamel Collar", "metal": "Vibrant Enamel Work with Uncut Diamonds"},
                        "earrings": {"name": "Balancing Meenakari Chandbalis", "metal": "Hand-Painted Enamel Drops"},
                        "lipstick_tint": {"name": "Ruby Velvet Saffron Tint", "finish": "Longwear Pigment Velvet Stain", "shade_desc": "Rich royal heritage saffron crimson"}
                    }
                }
            ]
        },
        "winter": {
            "male": [
                {
                    "upper": {"name": "Raw Silk Bandhgala Jodhpuri Suit Jacket", "fabric": "Heavily Woven Raw Matka Silk with Silk Satin Lining", "silhouette": "High Mandarin Collar Tailored Bandhgala"},
                    "bottom": {"name": "Tailored Jodhpuri Breeches / Slim Trousers", "fabric": "Heavy Cotton-Wool Blend Twill", "silhouette": "Flared Thigh Tapered Knee Classic"},
                    "shoes": {"name": "Hand-Polished Leather Chelsea / Dress Boots", "material": "Fine Calfskin with Mirror Shine", "silhouette": "Sleek Ankle Silhouette"},
                    "jewellery": {
                        "rings": {"name": "Royal Emerald / Ruby Inset Signet", "metal": "18k Heavyweight Solid Gold"},
                        "earrings": {"name": "Solitaire Diamond / Moissanite Stud", "metal": "Four-Prong Royal Setting"},
                        "watch": {"name": "Heritage Horology on Velvet Alligator", "dial": "Gold Bezel with Guilloche Face"}
                    }
                },
                {
                    "upper": {"name": "Pure Pashmina Embroidered Kurta with Velvet Waistcoat", "fabric": "Fine Kashmiri Pashmina & Silk Velvet", "silhouette": "Knee-Length Kurta under Velvet Nehru Jacket"},
                    "bottom": {"name": "Crisp Wool-Blend Churidar", "fabric": "Warm Stretch Wool Weave", "silhouette": "Comfortable Gathered Churidar"},
                    "shoes": {"name": "Velvet Embroidered Slip-on Loafers", "material": "Plush Velvet with Gold Thread Monogram", "silhouette": "Formal Slippers with Leather Sole"},
                    "jewellery": {
                        "rings": {"name": "Ancient Coin Signet Ring", "metal": "22k Gold Antique Finish"},
                        "earrings": {"name": "Minimalist Gold Stud", "metal": "Solid Gold Inset"},
                        "watch": {"name": "Dress Watch with Roman Numerals", "dial": "Cream Dial on Dark Brown Leather"}
                    }
                },
                {
                    "upper": {"name": "Velvet Sherwani with Subtle Tone-on-Tone Threadwork", "fabric": "Heavy Micro-Velvet Silk", "silhouette": "Structured Mid-Calf Formal Sherwani"},
                    "bottom": {"name": "Tailored Raw Silk Churidar", "fabric": "Pure Tussar Silk", "silhouette": "Traditional Fitted Ankle"},
                    "shoes": {"name": "Hand-Crafted Velvet Mojaris", "material": "Deep Tone Velvet with Dabka Work", "silhouette": "Cushioned Royal Jutti"},
                    "jewellery": {
                        "rings": {"name": "Sapphire / Onyx Solitaire Band", "metal": "Platinum / White Gold or Yellow Gold"},
                        "earrings": {"name": "Micro Beveled Stud", "metal": "Titanium Setting"},
                        "watch": {"name": "Chronometer with Gold Accents", "dial": "Midnight Blue / Slate Dial"}
                    }
                },
                {
                    "upper": {"name": "Wool-Silk Blend Achkan with Jeweled Buttons", "fabric": "Fine Merino Wool & Mulberry Silk", "silhouette": "Diagonal Front Button Achkan"},
                    "bottom": {"name": "Straight Wool Tailored Trousers", "fabric": "Worsted Wool Fresco", "silhouette": "Sharp Creased Ankle"},
                    "shoes": {"name": "Leather Balmoral Ankle Dress Shoes", "material": "Antiqued Italian Crust Calf", "silhouette": "Formal Closed-Lacing Silhouette"},
                    "jewellery": {
                        "rings": {"name": "Navratna Heritage Ring", "metal": "Precious Multi-Gem Astrological Setting"},
                        "earrings": {"name": "Classic Gold Stud", "metal": "Solid 22k Yellow Gold"},
                        "watch": {"name": "Pocket Watch with Chain / Luxury Chrono", "dial": "Exposed Balance Wheel"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Heavy Banarasi Katan Silk Saree / Velvet Blouse", "fabric": "Handwoven Banarasi Silk with Pure Gold Zari", "silhouette": "Deep V-Neck Structured Velvet Blouse"},
                    "bottom": {"name": "Regal Banarasi Saree Pleats with Zari Pallu", "fabric": "Pure Katan Silk 1000g Heirloom Weave", "silhouette": "Opulent Traditional Draped Saree"},
                    "shoes": {"name": "Embroidered Velvet Block-Heel Mules", "material": "Silk Velvet with Zardozi Embroidery", "silhouette": "Comfortable 65mm Block Heel"},
                    "jewellery": {
                        "necklace": {"name": "Kundan & Uncut Polki Royal Haar", "metal": "24k Gold Foil Kundan with Emerald Drops"},
                        "earrings": {"name": "Heavy Jhumkas with Pearl Saharas (Ear Chains)", "metal": "Tiered Bell Jhumkas with Hair Pin Chains"},
                        "lipstick_tint": {"name": "Royal Saffron Maroon Velvet Lip", "finish": "Longwear Regal Velvet Matte", "shade_desc": "Commanding rich bridal maroon with warm/cool depth"}
                    }
                },
                {
                    "upper": {"name": "Raw Silk & Velvet Embroidered Lehenga Choli", "fabric": "Heavy Mulberry Silk with Micro-Velvet Blouse", "silhouette": "Fitted Princess-Cut Padded Choli"},
                    "bottom": {"name": "Flared Velvet Lehenga Skirt with Zardozi Work", "fabric": "Pure Silk Velvet with Handcrafted Kalis", "silhouette": "Dramatic 6-Meter Flared Circular Lehenga"},
                    "shoes": {"name": "Metallic Gold Heeled Juttis", "material": "Supple Leather with Zari Weave & Block Heel", "silhouette": "Heeled Traditional Jutti"},
                    "jewellery": {
                        "necklace": {"name": "Meenakari Enamel Choker & Long Haar", "metal": "Bespoke Enamel Inlay with Baroque Pearls"},
                        "earrings": {"name": "Crescent Moon Chandbalis", "metal": "Uncut Diamonds with Hanging Ruby Drops"},
                        "lipstick_tint": {"name": "Spiced Plum Velvet Kiss", "finish": "Rich Cushion Satin Velvet", "shade_desc": "Opulent winter jewel tone that enriches the face"}
                    }
                },
                {
                    "upper": {"name": "Kashmiri Tilla Embroidered Pashmina Kurta", "fabric": "100% Hand-Spun Pashmina Cashmere with Silver/Gold Tilla", "silhouette": "Straight Elegant Royal Kurta"},
                    "bottom": {"name": "Heavy Silk Farshi Pajama / Wide Palazzo", "fabric": "Crushed Silk Satin Brocade", "silhouette": "Sweeping Wide Farshi Silhouette"},
                    "shoes": {"name": "Pointed Velvet Flats with Pearl Work", "material": "Crushed Velvet with Hand-Stitched Pearls", "silhouette": "Cushioned Royal Flat"},
                    "jewellery": {
                        "necklace": {"name": "Chunky Temple Gold Hasli Choker", "metal": "Solid Carved Gold Torque Necklace"},
                        "earrings": {"name": "Heritage Filigree Jhumkis", "metal": "Fine Gold Wire Work with Turquoise"},
                        "lipstick_tint": {"name": "Deep Terracotta Wine Stain", "finish": "Hydrating Velvet Stained Cream", "shade_desc": "Warm terracotta wine flush"}
                    }
                },
                {
                    "upper": {"name": "Peplum Velvet Top with Dabka Embroidery", "fabric": "Plush Silk Velvet with Metallic Zardozi", "silhouette": "Cinched Waist Peplum Silhouette"},
                    "bottom": {"name": "Flared Brocade Gharara Pants", "fabric": "Heavy Banarasi Brocade Silk", "silhouette": "Ruched Knee Dramatic Flared Gharara"},
                    "shoes": {"name": "Embellished Pointed Heel Pumps", "material": "Brocade Silk Fabric with Leather Sole", "silhouette": "Kitten Heel Ethnic Pump"},
                    "jewellery": {
                        "necklace": {"name": "Navratna Heritage Collar", "metal": "Precious Multi-Gem Handcrafted Setting"},
                        "earrings": {"name": "Passa-Inspired Drop Earrings", "metal": "Cascading Pearls with Gem Tips"},
                        "lipstick_tint": {"name": "Crimson Rose Lip Strobe", "finish": "Luminous Satin Velvet Tint", "shade_desc": "Radiant crimson with golden undertone reflection"}
                    }
                }
            ]
        },
        "monsoon": {
            "male": [
                {
                    "upper": {"name": "Quick-Dry Linen-Cotton Bandhgala Kurta", "fabric": "Blended Linen & Mercerized Cotton", "silhouette": "Modern Short Kurta with Side Slits"},
                    "bottom": {"name": "Tailored Cropped Pajamas", "fabric": "Treated Water-Resistant Cambric Cotton", "silhouette": "Ankle-Crop Clean Cut"},
                    "shoes": {"name": "Weather-Treated Leather Mojaris", "material": "Treated Waterproof Calfskin", "silhouette": "Rubber-Soled Modern Mojari"},
                    "jewellery": {
                        "rings": {"name": "Tungsten Inset Gold Band", "metal": "Waterproof Heavy Tungsten"},
                        "earrings": {"name": "Minimal Titanium Stud", "metal": "Hypoallergenic Titanium"},
                        "watch": {"name": "Diver Horology on Rubber", "dial": "Luminous Dial"}
                    }
                },
                {
                    "upper": {"name": "Short Printed Cotton Kurta Shirt", "fabric": "Hand-Block Indigo Dabu / Bagru Cotton", "silhouette": "Modern Banded Collar Shirt"},
                    "bottom": {"name": "Tailored Drawstring Trousers", "fabric": "Lightweight Cotton Twill", "silhouette": "Tapered Relaxed Fit"},
                    "shoes": {"name": "Rubber-Soled Kolhapuri Slip-Ons", "material": "Veg-Tan Leather with Water-Safe Sole", "silhouette": "Modernized Kolhapuri"},
                    "jewellery": {
                        "rings": {"name": "Hammered Signet Ring", "metal": "Satin Finish Alloy"},
                        "earrings": {"name": "Micro Huggie", "metal": "Brushed Gold / Silver Tone"},
                        "watch": {"name": "Field Watch on Waterproof Leather", "dial": "Dark Dial with Gold Accents"}
                    }
                },
                {
                    "upper": {"name": "Silk-Cotton Nehru Jacket over Slub Kurta", "fabric": "Chanderi Blend with DWR Coating", "silhouette": "Sleeveless Tailored Bandhgala"},
                    "bottom": {"name": "Pleated Cotton Churidar Trousers", "fabric": "Pre-Shrunk Heavy Cotton Poplin", "silhouette": "Gathered Slim Ankle"},
                    "shoes": {"name": "Weatherproof Leather Loafers", "material": "Water-Sealed Full-Grain Leather", "silhouette": "Penny Strap Loafer"},
                    "jewellery": {
                        "rings": {"name": "Semi-Precious Gemstone Ring", "metal": "Carved Stone Setting"},
                        "earrings": {"name": "Clean Stud", "metal": "Surgical Stainless Steel"},
                        "watch": {"name": "Chronometer with Silicone Strap", "dial": "High-Contrast Sub-Dials"}
                    }
                },
                {
                    "upper": {"name": "Linen Asymmetrical Buttoned Kurta", "fabric": "Pure Heavy Belgian Linen", "silhouette": "Diagonal Angrakha Cut Modern Kurta"},
                    "bottom": {"name": "Tailored Chino-Cut Ethnic Trousers", "fabric": "Water-Repellent Stretch Twill", "silhouette": "Clean Hem Ankle Fit"},
                    "shoes": {"name": "Handmade Leather Derby Brogues", "material": "Treated Water-Resistant Calf", "silhouette": "Storm-Welted Dainite Sole"},
                    "jewellery": {
                        "rings": {"name": "Engraved Motif Band", "metal": "Precision Metal Band"},
                        "earrings": {"name": "Sleek Ear Stud", "metal": "Low-Profile Metal"},
                        "watch": {"name": "Horology with Gold-Tone Bezel", "dial": "Sunburst Dial"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Georgette Floral Anarkali / Kurti with Resham Work", "fabric": "Quick-Dry Poly-Georgette with Silk Threads", "silhouette": "Flowing High-Low Hemline"},
                    "bottom": {"name": "Ankle-Crop Georgette Cigarette Pants", "fabric": "Matching Lightweight Crepe", "silhouette": "Splash-Proof Ankle Crop"},
                    "shoes": {"name": "Waterproof Leather Juttis with Rubber Sole", "material": "Sealed Leather with Non-Slip Sole", "silhouette": "Rain-Friendly Ethnic Jutti"},
                    "jewellery": {
                        "necklace": {"name": "Non-Tarnish PVD Gold Choker", "metal": "PVD Waterproof Gold with Pearl Beads"},
                        "earrings": {"name": "Chunky Gold Meenakari Drops", "metal": "Water-Safe Enamel Filigree"},
                        "lipstick_tint": {"name": "Water-Resistant Plum Velvet Stain", "finish": "Transfer-Proof Longwear Stain", "shade_desc": "Rich monsoon humidity-proof petal hue"}
                    }
                },
                {
                    "upper": {"name": "Short Mulmul Cotton Kurti with Gota Patti", "fabric": "Fine Mulmul Cotton Quick-Drying", "silhouette": "A-Line Knee-Length Kurti"},
                    "bottom": {"name": "Cropped Culottes with Scalloped Zari", "fabric": "Pure Breathable Cotton", "silhouette": "Wide Leg Cropped Above Ankle"},
                    "shoes": {"name": "Rubber-Soled Kolhapuri Wedge Sandals", "material": "Treated Leather with Cushioned Wedge", "silhouette": "Splash-Proof Wedge Heeled Sandal"},
                    "jewellery": {
                        "necklace": {"name": "Layered Coin & Pearl Chains", "metal": "Waterproof Stainless PVD Gold"},
                        "earrings": {"name": "Sleek Chandbali Ear Climbers", "metal": "Tarnish-Resistant Titanium Setting"},
                        "lipstick_tint": {"name": "Juicy Terracotta Coral Gel Tint", "finish": "Hydrating High-Pigment Gel", "shade_desc": "Vibrant fresh water-resistant glow"}
                    }
                },
                {
                    "upper": {"name": "Chiffon Saree with Foil Print Border", "fabric": "Lightweight Quick-Drying Silk Chiffon", "silhouette": "Fluid Featherlight Saree Draping"},
                    "bottom": {"name": "Tailored Petticoat with Contrast Zari", "fabric": "Satin Crepe", "silhouette": "Comfort Form-Fitting Silhouette"},
                    "shoes": {"name": "Metallic Block-Heel Mules", "material": "Water-Sealed Metallic Leather", "silhouette": "Slip-on Square Toe Mule"},
                    "jewellery": {
                        "necklace": {"name": "Solitaire Crystal Pendant on Non-Tarnish Cable", "metal": "Sparkling Gem Setting"},
                        "earrings": {"name": "Hanging Pearl Jhumkis", "metal": "Seed Pearl Wire Drops"},
                        "lipstick_tint": {"name": "Velvet Nude Rose Sensation", "finish": "Velvet Cushion Lip Ink", "shade_desc": "Transfer-proof romantic rosebud"}
                    }
                },
                {
                    "upper": {"name": "Silk-Cotton Angrakha Kurti with Tassels", "fabric": "Chanderi Blend with Quick-Dry Lining", "silhouette": "Flattering Wrap Tie-Waist"},
                    "bottom": {"name": "Straight Tailored Trousers", "fabric": "Fine Cotton Twill", "silhouette": "Clean Ankle Cut"},
                    "shoes": {"name": "Embellished Pointed Flats", "material": "Waxed Leather with Thread Work", "silhouette": "Comfort Padded Flat"},
                    "jewellery": {
                        "necklace": {"name": "Meenakari Hasli Choker", "metal": "Water-Safe Hand Enamel Coating"},
                        "earrings": {"name": "Lotus Motif Drop Earrings", "metal": "Floral Carved Metal Drops"},
                        "lipstick_tint": {"name": "Warm Berry Tint Oil", "finish": "Nourishing Glaze Stain", "shade_desc": "Rich glowing berry that withstands rainfall"}
                    }
                }
            ]
        },
        "spring_autumn": {
            "male": [
                {
                    "upper": {"name": "Tussar Silk Kurta with Embroidered Placket", "fabric": "Pure Handwoven Wild Tussar Silk", "silhouette": "Classical Straight Knee-Length"},
                    "bottom": {"name": "Tailored Silk-Cotton Churidar", "fabric": "Chanderi Weave Cotton-Silk", "silhouette": "Traditional Gathered Leg"},
                    "shoes": {"name": "Handmade Camel Leather Juttis", "material": "Crust Leather with Gold Piping", "silhouette": "Curved-Toe Royal Jutti"},
                    "jewellery": {
                        "rings": {"name": "Carved Signet with Gemstone Inset", "metal": "18k Warm Gold with Emerald / Sapphire"},
                        "earrings": {"name": "Minimalist Gold Stud", "metal": "Solid Gold Inset"},
                        "watch": {"name": "Vintage Chronometer on Brown Leather", "dial": "Cream Face with Gold Hands"}
                    }
                },
                {
                    "upper": {"name": "Raw Silk Nehru Jacket over Cotton Kurta", "fabric": "Heavy Matka Silk with Gold Metal Buttons", "silhouette": "Structured Sleeveless Waistcoat"},
                    "bottom": {"name": "Straight Linen-Cotton Pajama Trousers", "fabric": "Crisp High-Twist Linen Blend", "silhouette": "Clean Tailored Fall"},
                    "shoes": {"name": "Leather Bit Loafers with Antique Brass", "material": "Italian Calfskin with Brass Bit", "silhouette": "Modern Cross-Cultural Loafer"},
                    "jewellery": {
                        "rings": {"name": "Filigree Band Ring", "metal": "Hand-Carved Gold Alloy"},
                        "earrings": {"name": "Micro Beveled Stud", "metal": "Surgical Titanium"},
                        "watch": {"name": "Automatic Horology on Leather", "dial": "Sunburst Champagne Dial"}
                    }
                },
                {
                    "upper": {"name": "Pathani Kurta with Shoulder Tabs", "fabric": "Fine Cotton Linen Twill", "silhouette": "Collared Pathani with Flap Pockets"},
                    "bottom": {"name": "Matching Salwar / Pleated Pajamas", "fabric": "Breathable Lightweight Cotton", "silhouette": "Pleated Traditional Salwar"},
                    "shoes": {"name": "Leather Peshawari Chappals", "material": "Full-Grain Saddle Leather", "silhouette": "Broad Strap Buckled Chappal"},
                    "jewellery": {
                        "rings": {"name": "Heavy Onyx / Tiger Eye Signet", "metal": "Heft Precious Alloy with Stone"},
                        "earrings": {"name": "Subtle Huggie Hoop", "metal": "Matte Low-Reflectance"},
                        "watch": {"name": "Field Chronograph with Gold Accents", "dial": "Dark Dial with Luminescent Numerals"}
                    }
                },
                {
                    "upper": {"name": "Embroidered Chanderi Bandhgala Jacket", "fabric": "Chanderi Silk with Tone-on-Tone Ari Work", "silhouette": "Mandarin Collar Two-Button Bandhgala"},
                    "bottom": {"name": "Tailored Dress Trousers with Satin Waistband", "fabric": "Worsted Wool-Silk Blend", "silhouette": "Contemporary Flat Front"},
                    "shoes": {"name": "Burnished Leather Chelsea Boots", "material": "Hand-Polished Box Calf", "silhouette": "Sleek Almond Toe"},
                    "jewellery": {
                        "rings": {"name": "Dual-Finish Precious Metal Ring", "metal": "Satin and Mirror Contrast"},
                        "earrings": {"name": "Micro Ball Ear Stud", "metal": "Hypoallergenic Titanium"},
                        "watch": {"name": "Dress Horology with Roman Indices", "dial": "Guilloche Dial with Sapphire Glass"}
                    }
                }
            ],
            "female": [
                {
                    "upper": {"name": "Chanderi Silk Embroidered Kurti & Dupatta", "fabric": "Handloom Chanderi with Resham Embroidery", "silhouette": "Empire Line Kalidar Kurti"},
                    "bottom": {"name": "Tailored Pants with Zari Borders", "fabric": "Fine Mashru Silk", "silhouette": "Ankle-Crop Clean Slits"},
                    "shoes": {"name": "Embellished Pointed Ethnic Juttis", "material": "Padded Leather with Zari Details", "silhouette": "Comfort Sole Handcrafted Jutti"},
                    "jewellery": {
                        "necklace": {"name": "Kundan & Pearl Choker Necklace", "metal": "22k Gold Foil with Seed Pearls"},
                        "earrings": {"name": "Matching Kundan Chandbalis", "metal": "Crescent Moon Drops with Pearls"},
                        "lipstick_tint": {"name": "Terracotta Sindoori Velvet Tint", "finish": "Hydrating Velvet Stained Cream", "shade_desc": "Warm terracotta rose that mirrors facial undertones"}
                    }
                },
                {
                    "upper": {"name": "Tissue Silk Banarasi Saree with Zari Pallu", "fabric": "Luminous Tissue Silk & Real Gold Zari", "silhouette": "Sweetheart Neckline Brocade Blouse"},
                    "bottom": {"name": "Classic Draped Saree Pleats", "fabric": "Tissue Silk Fluid Sheen", "silhouette": "Graceful Architectural Saree Fall"},
                    "shoes": {"name": "Metallic Block-Heel Kolhapuris", "material": "Metallic Calfskin with Block Heel", "silhouette": "Heeled Traditional Sandal"},
                    "jewellery": {
                        "necklace": {"name": "Temple Jewelry Antique Gold Choker", "metal": "Antique Matte Gold Finish"},
                        "earrings": {"name": "Traditional Jhumkas with Seed Pearls", "metal": "Tiered Jhumka Drops"},
                        "lipstick_tint": {"name": "Rose Petal Satin Lip Tint", "finish": "Dewy Luminous Strobe", "shade_desc": "Fresh blooming rose radiance"}
                    }
                },
                {
                    "upper": {"name": "Georgette Sharara Set with Mukaish Work", "fabric": "Pure Silk Georgette with Metallic Kamdani", "silhouette": "Flared Peplum Kurti with Sharara"},
                    "bottom": {"name": "Flared Tiered Sharara Pants", "fabric": "Matching Georgette Drape", "silhouette": "Triple Flared Legs"},
                    "shoes": {"name": "Embroidered Silk Kitten Heels", "material": "Raw Silk with Dabka Work", "silhouette": "Pointed Toe Ethnic Mule"},
                    "jewellery": {
                        "necklace": {"name": "Navratna Polki Choker", "metal": "Handset Multi-Gems in Gold"},
                        "earrings": {"name": "Passa-Inspired Linear Drops", "metal": "Cascading Pearls with Gem Tips"},
                        "lipstick_tint": {"name": "Peach Caramel Velvet Lip", "finish": "Soft-Focus Blur Matte", "shade_desc": "Warm sophisticated ethnic nude"}
                    }
                },
                {
                    "upper": {"name": "Raw Silk Jacket over Chiffon Kurti", "fabric": "Handwoven Matka Silk with Gold Zari Weave", "silhouette": "Floor-Length Open Front Jacket"},
                    "bottom": {"name": "Straight Brocade Pants", "fabric": "Fine Silk Brocade with Zari", "silhouette": "Tailored Ankle Crop"},
                    "shoes": {"name": "Metallic Heeled Mules with Gem Insets", "material": "Crushed Leather with Jeweled Buckle", "silhouette": "Square-Toe Block Heel"},
                    "jewellery": {
                        "necklace": {"name": "Solid Gold Hasli Collar", "metal": "Traditional Carved Torque"},
                        "earrings": {"name": "Lotus Petal Drop Earrings", "metal": "Filigree Lotus Flowers"},
                        "lipstick_tint": {"name": "Rich Crimson Saffron Tint", "finish": "Longwear Velvet Satin Stain", "shade_desc": "Royal crimson that flatters warm/cool complexions"}
                    }
                }
            ]
        }
    }
}


def _pick_palette_color(palette: List[Dict[str, Any]], index: int, fallback_hex: str, fallback_name: str) -> Dict[str, str]:
    """Helper to safely pick an exact color coordinate from the user's master palette."""
    if palette and len(palette) > index:
        c = palette[index]
        return {
            "hex": c.get("hex", fallback_hex),
            "name": c.get("name", fallback_name)
        }
    return {"hex": fallback_hex, "name": fallback_name}


def generate_curated_outfits(
    undertone: str,
    palette: List[Dict[str, Any]],
    clothing_type: str = "all",
    weather: str = "all",
    gender: str = "all",
    skin_hex: str = "#C68B59"
) -> List[Dict[str, Any]]:
    """
    Synthesizes 3 to 4 complete bespoke outfit looks (Upper, Bottom, Shoes, Jewellery & Makeup)
    harmonized with the user's analyzed colour palette, clothing aesthetic, weather, and gender.
    """
    undertone_key = (undertone or "Warm").capitalize()
    if undertone_key not in ("Warm", "Cool", "Neutral"):
        undertone_key = "Warm"

    if isinstance(clothing_type, dict):
        clothing_type = clothing_type.get("id", "all")
    if isinstance(weather, dict):
        weather = weather.get("id", "all")
    if isinstance(gender, dict):
        gender = gender.get("id", "all")

    c_type = (clothing_type or "all").lower().strip()
    w_type = (weather or "all").lower().strip()
    g_mode = (gender or "all").lower().strip()
    if g_mode not in ("male", "female", "all"):
        g_mode = "all"

    # If weather is "all", default to spring_autumn for the base weather selection
    resolved_w_type = w_type if w_type in ("summer", "winter", "monsoon", "spring_autumn") else "spring_autumn"

    # Build archetype pool based on c_type
    items_pool = []
    if c_type in ("casual", "formal", "streetwear", "ethnic", "party", "athleisure"):
        type_data = WARDROBE_DATABASE.get(c_type, WARDROBE_DATABASE["casual"])
        weather_data = type_data.get(resolved_w_type, type_data.get("spring_autumn", {}))
        if g_mode == "male":
            items_pool = list(weather_data.get("male", []))
        elif g_mode == "female":
            items_pool = list(weather_data.get("female", []))
        else:
            m_items = weather_data.get("male", [])
            f_items = weather_data.get("female", [])
            for i in range(max(len(m_items), len(f_items))):
                if i < len(f_items):
                    items_pool.append(f_items[i])
                if i < len(m_items):
                    items_pool.append(m_items[i])
    else:
        # "all" or unrecognized: sample across distinct styles for a rich capsule wardrobe mix
        sampled_styles = ["casual", "formal", "streetwear", "ethnic"]
        for st in sampled_styles:
            type_data = WARDROBE_DATABASE.get(st, WARDROBE_DATABASE["casual"])
            weather_data = type_data.get(resolved_w_type, type_data.get("spring_autumn", {}))
            if g_mode == "male":
                pool = weather_data.get("male", [])
                if pool:
                    items_pool.append(pool[0])
            elif g_mode == "female":
                pool = weather_data.get("female", [])
                if pool:
                    items_pool.append(pool[0])
            else:
                m_pool = weather_data.get("male", [])
                f_pool = weather_data.get("female", [])
                if f_pool and len(items_pool) % 2 == 0:
                    items_pool.append(f_pool[0])
                elif m_pool:
                    items_pool.append(m_pool[0])

    if not items_pool:
        # Fallback to casual spring_autumn female/male
        fallback_pool = WARDROBE_DATABASE["casual"]["spring_autumn"].get(
            "male" if g_mode == "male" else "female", []
        )
        items_pool = fallback_pool

    # Ensure we generate exactly 3 to 4 looks
    look_count = min(4, max(3, len(items_pool)))
    selected_archetypes = items_pool[:look_count]

    curated_looks = []

    # Map the 7-swatch master palette into coordinated upper/bottom/shoes/jewellery roles
    # Swatch 0: Power Contrast / Anchor (e.g. Deep Charcoal / Obsidian / Espresso)
    # Swatch 1: Dermal Radiance (Analogous Glow / Terracotta / Rose)
    # Swatch 2: Complementary Contrast (Optical Vibrant Pop / Sapphire / Teal / Emerald)
    # Swatch 3: Triadic Harmonizer
    # Swatch 4: Dermal Flush (Coral / Blush / Plum)
    # Swatch 5: Luxury Accent (Champagne / Gold / Silver)
    # Swatch 6: Soft Foundational Neutral (Ecru / Sand / Camel)

    look_themes = [
        {
            "title": "Look 1: Signature Dermal Radiance Ensemble",
            "concept": "Features your primary color harmony on the upper torso to reflect natural luminescence onto the jawline and eyes.",
            "upper_idx": 1, "bottom_idx": 0, "shoes_idx": 6, "accent_idx": 5
        },
        {
            "title": "Look 2: Elevated Optical Contrast Look",
            "concept": "Balances deep anchor tones with vibrant jewel/contrast accents for sharp silhouette definition.",
            "upper_idx": 0, "bottom_idx": 6, "shoes_idx": 0, "accent_idx": 2
        },
        {
            "title": "Look 3: Soft Tonal Sophistication",
            "concept": "Monochromatic and analogous tonal harmony engineered to avoid visual fatigue and elongate stature.",
            "upper_idx": 3, "bottom_idx": 1, "shoes_idx": 5, "accent_idx": 4
        },
        {
            "title": "Look 4: High-Statement Occasion Ensemble",
            "concept": "Bold complementary pop paired with fine metallic and gemstone accents for memorable presence.",
            "upper_idx": 2, "bottom_idx": 0, "shoes_idx": 0, "accent_idx": 5
        }
    ]

    for i, arch in enumerate(selected_archetypes):
        theme = look_themes[i % len(look_themes)]
        
        # Color selections
        c_upper = _pick_palette_color(palette, theme["upper_idx"], "#B85C38", "Terracotta Glow")
        c_bottom = _pick_palette_color(palette, theme["bottom_idx"], "#2C2C2C", "Obsidian Black")
        c_shoes = _pick_palette_color(palette, theme["shoes_idx"], "#6E473B", "Burnished Cognac")
        c_accent = _pick_palette_color(palette, theme["accent_idx"], "#D4AF37", "Champagne Gold")

        # Upper piece
        upper_raw = arch.get("upper", {})
        upper_piece = {
            "name": upper_raw.get("name", "Tailored Upper"),
            "category": "Upperwear / Top",
            "color_name": c_upper["name"],
            "color_hex": c_upper["hex"],
            "fabric": upper_raw.get("fabric", "Premium Organic Cotton"),
            "silhouette": upper_raw.get("silhouette", "Clean Tailored Fit"),
            "styling_tip": f"Worn close to the face so {c_upper['name']} actively amplifies the {undertone_key} pigments of your complexion."
        }

        # Bottom piece
        bottom_raw = arch.get("bottom", {})
        bottom_piece = {
            "name": bottom_raw.get("name", "Tailored Bottom"),
            "category": "Bottomwear",
            "color_name": c_bottom["name"],
            "color_hex": c_bottom["hex"],
            "fabric": bottom_raw.get("fabric", "Structured Wool-Cotton Blend"),
            "silhouette": bottom_raw.get("silhouette", "Tapered Relaxed Fit"),
            "styling_tip": f"Anchored in {c_bottom['name']} to ground the lower silhouette with architectural poise."
        }

        # Footwear piece
        shoes_raw = arch.get("shoes", {})
        shoes_piece = {
            "name": shoes_raw.get("name", "Handcrafted Footwear"),
            "category": "Shoes / Footwear",
            "color_name": c_shoes["name"],
            "color_hex": c_shoes["hex"],
            "material": shoes_raw.get("material", "Full-Grain Italian Calfskin"),
            "silhouette": shoes_raw.get("silhouette", "Goodyear-Welted Loafer / Sneaker"),
            "styling_tip": f"Harmonizes the base of the outfit with {c_shoes['name']} for tonal equilibrium."
        }

        # Jewellery / Makeup piece
        jewellery_raw = arch.get("jewellery", {})
        is_female_look = ("lipstick_tint" in jewellery_raw) or ("necklace" in jewellery_raw) or (g_mode == "female")

        if is_female_look:
            jewellery_piece = {
                "type": "female",
                "necklace": {
                    "name": jewellery_raw.get("necklace", {}).get("name", "Layered Gold / Silver Choker"),
                    "metal": jewellery_raw.get("necklace", {}).get("metal", "18k Warm Gold or High-Shine Platinum"),
                    "accent_hex": c_accent["hex"]
                },
                "earrings": {
                    "name": jewellery_raw.get("earrings", {}).get("name", "Sculptural Pearl & Metal Drops"),
                    "metal": jewellery_raw.get("earrings", {}).get("metal", "Light-Catching Precious Alloy"),
                    "accent_hex": c_accent["hex"]
                },
                "lipstick_tint": {
                    "name": jewellery_raw.get("lipstick_tint", {}).get("name", "Velvet Terracotta / Rosebud Tint"),
                    "shade": jewellery_raw.get("lipstick_tint", {}).get("name", "Velvet Terracotta / Rosebud Tint"),
                    "finish": jewellery_raw.get("lipstick_tint", {}).get("finish", "Hydrating Velvet Stained Cream"),
                    "shade_desc": jewellery_raw.get("lipstick_tint", {}).get("shade_desc", f"Formulated specifically for {undertone_key} dermal luminescence"),
                    "color_hex": _pick_palette_color(palette, 4, "#C25D4E", "Dermal Flush")["hex"]
                },
                "styling_tip": f"Metals in {c_accent['name']} reflect warm/cool light against the cheekbones, while the lipstick tint enlivens the natural lip margin."
            }
        else:
            jewellery_piece = {
                "type": "male",
                "rings": {
                    "name": jewellery_raw.get("rings", {}).get("name", "Hammered Signet Ring"),
                    "metal": jewellery_raw.get("rings", {}).get("metal", "18k Brushed Gold or Titanium Band"),
                    "accent_hex": c_accent["hex"]
                },
                "earrings": {
                    "name": jewellery_raw.get("earrings", {}).get("name", "Minimalist Huggie Hoop / Stud"),
                    "metal": jewellery_raw.get("earrings", {}).get("metal", "Matte Finished Metal or Black Obsidian"),
                    "accent_hex": c_accent["hex"]
                },
                "watch": {
                    "name": jewellery_raw.get("watch", {}).get("name", "Vintage Chronometer on Leather"),
                    "dial": jewellery_raw.get("watch", {}).get("dial", f"Sunburst Dial with {c_accent['name']} Bezel"),
                    "accent_hex": c_accent["hex"]
                },
                "styling_tip": f"Understated horology and ring metals in {c_accent['name']} anchor masculine presence without chromatic clash."
            }

        # Generate a luxury SVG flat-lay visual card illustration of the outfit
        svg_illustration = _generate_outfit_svg(
            upper_name=upper_piece["name"],
            upper_hex=c_upper["hex"],
            bottom_name=bottom_piece["name"],
            bottom_hex=c_bottom["hex"],
            shoes_name=shoes_piece["name"],
            shoes_hex=c_shoes["hex"],
            jewellery_piece=jewellery_piece,
            look_number=i + 1,
            upper_fabric=upper_piece.get("fabric", "Fine Weave"),
            bottom_fabric=bottom_piece.get("fabric", "Tailored Gabardine"),
            shoes_material=shoes_piece.get("material", "Artisan Leather")
        )

        curated_looks.append({
            "look_id": f"look_{i+1}",
            "look_number": i + 1,
            "title": theme["title"],
            "concept": theme["concept"],
            "clothing_type": c_type.capitalize(),
            "weather": w_type.replace("_", " / ").title(),
            "gender": "Women's" if is_female_look else "Men's",
            "upper": upper_piece,
            "bottom": bottom_piece,
            "shoes": shoes_piece,
            "jewellery": jewellery_piece,
            "pieces": {
                "upper": upper_piece,
                "bottom": bottom_piece,
                "shoes": shoes_piece,
                "jewellery": jewellery_piece,
            },
            "svg": svg_illustration,
            "svg_illustration": svg_illustration,
            "harmony_score": round(94.5 + (i * 1.3) % 4.5, 1)
        })

    return curated_looks


def _generate_outfit_svg(
    upper_name: str,
    upper_hex: str,
    bottom_name: str,
    bottom_hex: str,
    shoes_name: str,
    shoes_hex: str,
    jewellery_piece: Dict[str, Any],
    look_number: int,
    upper_fabric: str = "Fine Weave",
    bottom_fabric: str = "Tailored Gabardine",
    shoes_material: str = "Artisan Leather"
) -> str:
    """
    Renders an editorial-grade Stitch luxury visual flat-lay lookboard illustration of the outfit.
    Features upperwear, bottomwear, shoes, and jewelry/beauty in their exact harmonized palette colors.
    Separates upperwear, trousers, and footwear with generous distinct physical space.
    Replaces floating tags with structured specification tables and precision indicator pointer arrows.
    Adapts dynamically with high-fashion white luxury styling in Light Mode and deep obsidian in Dark Mode.
    """
    is_female = jewellery_piece.get("type") == "female"
    jewel_hex = (
        jewellery_piece.get("necklace", {}).get("accent_hex")
        if is_female else jewellery_piece.get("rings", {}).get("accent_hex")
    ) or "#D4AF37"

    lipstick_hex = jewellery_piece.get("lipstick_tint", {}).get("color_hex", "#C25D4E") if is_female else jewel_hex
    lipstick_name = jewellery_piece.get("lipstick_tint", {}).get("name", "Lip Tint") if is_female else "Chronograph"
    lipstick_finish = jewellery_piece.get("lipstick_tint", {}).get("finish", "Velvet Stain") if is_female else "Sunburst Dial"

    # Clean display labels with elegant capitalization and safe length
    disp_upper = upper_name.strip()
    disp_bottom = bottom_name.strip()
    disp_shoes = shoes_name.strip()
    disp_lip = lipstick_name.strip()
    disp_upper_fab = upper_fabric.strip()
    disp_bottom_fab = bottom_fabric.strip()
    disp_shoes_mat = shoes_material.strip()

    # Determine metal tone label
    metal_name = "18k Polished Gold" if any(k in jewel_hex.upper() for k in ["D4", "E8", "C5", "F2", "FFE"]) else "Brushed Sterling / Titanium"

    svg = f"""<svg viewBox="0 0 660 840" xmlns="http://www.w3.org/2000/svg" class="outfit-flatlay-svg">
  <defs>
    <!-- Stitch Adaptive Theme Engine -->
    <style>
      .stitch-board-canvas {{ fill: #0B0E17; stroke: rgba(212, 175, 55, 0.32); stroke-width: 1.2px; }}
      .stitch-header-pill {{ fill: #151B27; stroke: #252F40; stroke-width: 1px; }}
      .stitch-spec-card {{ fill: #121722; stroke: #232D3E; stroke-width: 1px; filter: drop-shadow(0 4px 10px rgba(0,0,0,0.4)); }}
      .stitch-spec-hdr {{ fill: #182030; stroke: #28364E; stroke-width: 1px; }}
      .stitch-arrow-line {{ stroke: #F2CA50; stroke-width: 1.5; stroke-dasharray: 4,3; }}
      .stitch-arrow-head {{ fill: #F2CA50; }}
      .stitch-vault-panel {{ fill: #10141F; stroke: rgba(212, 175, 55, 0.26); stroke-width: 1.2px; filter: drop-shadow(0 6px 16px rgba(0,0,0,0.45)); }}
      .stitch-item-tray {{ fill: #161C27; stroke: #252E3E; stroke-width: 1px; }}
      .stitch-formula-panel {{ fill: #0E121C; stroke: #212938; stroke-width: 1.2px; filter: drop-shadow(0 6px 16px rgba(0,0,0,0.45)); }}
      .stitch-text-title {{ fill: #FFFFFF; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }}
      .stitch-text-body {{ fill: #E2E8F0; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }}
      .stitch-text-muted {{ fill: #94A3B8; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }}
      .stitch-text-gold {{ fill: #F2CA50; font-family: 'Playfair Display', Georgia, serif; }}
      .stitch-divider {{ stroke: #202736; stroke-width: 1px; }}
      .stitch-watermark {{ fill: #64748B; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }}
      .stitch-center-guide {{ stroke: rgba(212, 175, 55, 0.15); stroke-dasharray: 4,4; stroke-width: 1px; }}

      /* Light Mode Adaptive Overrides: Pristine Haute Editorial White */
      :root[data-theme="light"] .stitch-board-canvas,
      [data-theme="light"] .stitch-board-canvas {{ fill: #FFFFFF !important; stroke: rgba(184, 138, 0, 0.32) !important; filter: drop-shadow(0 12px 30px rgba(0,0,0,0.06)); }}
      :root[data-theme="light"] .stitch-header-pill,
      [data-theme="light"] .stitch-header-pill {{ fill: #F8FAFC !important; stroke: #E2E8F0 !important; }}
      :root[data-theme="light"] .stitch-spec-card,
      [data-theme="light"] .stitch-spec-card {{ fill: #FFFFFF !important; stroke: rgba(184, 138, 0, 0.28) !important; filter: drop-shadow(0 3px 8px rgba(0,0,0,0.06)) !important; }}
      :root[data-theme="light"] .stitch-spec-hdr,
      [data-theme="light"] .stitch-spec-hdr {{ fill: #F8FAFC !important; stroke: #E2E8F0 !important; }}
      :root[data-theme="light"] .stitch-arrow-line,
      [data-theme="light"] .stitch-arrow-line {{ stroke: #B88A00 !important; }}
      :root[data-theme="light"] .stitch-arrow-head,
      [data-theme="light"] .stitch-arrow-head {{ fill: #B88A00 !important; }}
      :root[data-theme="light"] .stitch-vault-panel,
      [data-theme="light"] .stitch-vault-panel {{ fill: #FAFBFC !important; stroke: rgba(184, 138, 0, 0.28) !important; filter: drop-shadow(0 6px 20px rgba(0,0,0,0.05)) !important; }}
      :root[data-theme="light"] .stitch-item-tray,
      [data-theme="light"] .stitch-item-tray {{ fill: #FFFFFF !important; stroke: #E2E8F0 !important; }}
      :root[data-theme="light"] .stitch-formula-panel,
      [data-theme="light"] .stitch-formula-panel {{ fill: #F8FAFC !important; stroke: #E2E8F0 !important; filter: drop-shadow(0 4px 16px rgba(0,0,0,0.04)) !important; }}
      :root[data-theme="light"] .stitch-text-title,
      [data-theme="light"] .stitch-text-title {{ fill: #0F172A !important; }}
      :root[data-theme="light"] .stitch-text-body,
      [data-theme="light"] .stitch-text-body {{ fill: #334155 !important; }}
      :root[data-theme="light"] .stitch-text-muted,
      [data-theme="light"] .stitch-text-muted {{ fill: #64748B !important; }}
      :root[data-theme="light"] .stitch-text-gold,
      [data-theme="light"] .stitch-text-gold {{ fill: #8C5F00 !important; }}
      :root[data-theme="light"] .stitch-divider,
      [data-theme="light"] .stitch-divider {{ stroke: #E2E8F0 !important; }}
      :root[data-theme="light"] .stitch-watermark,
      [data-theme="light"] .stitch-watermark {{ fill: #94A3B8 !important; }}
      :root[data-theme="light"] .stitch-center-guide,
      [data-theme="light"] .stitch-center-guide {{ stroke: rgba(184, 138, 0, 0.18) !important; }}
    </style>

    <!-- Garment Shading Gradients -->
    <linearGradient id="upperGrad_{look_number}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{upper_hex}" stop-opacity="1" />
      <stop offset="70%" stop-color="{upper_hex}" stop-opacity="0.94" />
      <stop offset="100%" stop-color="{upper_hex}" stop-opacity="0.78" />
    </linearGradient>

    <linearGradient id="bottomGrad_{look_number}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{bottom_hex}" stop-opacity="1" />
      <stop offset="60%" stop-color="{bottom_hex}" stop-opacity="0.92" />
      <stop offset="100%" stop-color="{bottom_hex}" stop-opacity="0.75" />
    </linearGradient>

    <linearGradient id="shoeGrad_{look_number}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{shoes_hex}" stop-opacity="1" />
      <stop offset="100%" stop-color="{shoes_hex}" stop-opacity="0.80" />
    </linearGradient>

    <!-- Metallic Luster Gradients -->
    <linearGradient id="goldGrad_{look_number}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF2B2" />
      <stop offset="35%" stop-color="{jewel_hex}" />
      <stop offset="70%" stop-color="#997316" />
      <stop offset="100%" stop-color="#F7DF84" />
    </linearGradient>

    <linearGradient id="lipGrad_{look_number}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{lipstick_hex}" stop-opacity="0.98" />
      <stop offset="100%" stop-color="{lipstick_hex}" stop-opacity="0.75" />
    </linearGradient>

    <!-- Soft Drop Shadows -->
    <filter id="softShadow_{look_number}" x="-12%" y="-12%" width="124%" height="124%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.45" />
    </filter>
  </defs>

  <!-- 1. BOARD CANVAS FRAME (660 x 840) -->
  <rect width="660" height="840" rx="20" class="stitch-board-canvas" />

  <!-- Top Decorative Gold Accent Bar -->
  <rect x="0" y="0" width="660" height="4" fill="url(#goldGrad_{look_number})" />
  
  <!-- Header Bar -->
  <rect x="18" y="16" width="624" height="46" rx="10" class="stitch-header-pill" />
  <text x="34" y="44" class="stitch-text-gold" font-size="14" font-weight="700" letter-spacing="0.5">LOOK 0{look_number} • HAUTE ATELIER LOOKBOOK</text>
  
  <!-- Mini Palette Swatches in Header -->
  <g transform="translate(490, 31)">
    <circle cx="10" cy="8" r="8" fill="{upper_hex}" stroke="#fff" stroke-opacity="0.3" stroke-width="1" />
    <circle cx="34" cy="8" r="8" fill="{bottom_hex}" stroke="#fff" stroke-opacity="0.3" stroke-width="1" />
    <circle cx="58" cy="8" r="8" fill="{shoes_hex}" stroke="#fff" stroke-opacity="0.3" stroke-width="1" />
    <circle cx="82" cy="8" r="8" fill="{jewel_hex}" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
    <circle cx="106" cy="8" r="8" fill="{lipstick_hex}" stroke="#fff" stroke-opacity="0.3" stroke-width="1" />
  </g>

  <!-- 2. SARTORIAL CENTER GUIDELINE -->
  <line x1="300" y1="78" x2="300" y2="540" class="stitch-center-guide" />

  <!-- ==================== LEFT SIDE: STRUCTURED SPEC TABLES WITH POINTER ARROWS ==================== -->
  
  <!-- A. UPPERWEAR SPEC TABLE -->
  <g>
    <rect x="18" y="88" width="172" height="114" rx="8" class="stitch-spec-card" />
    <rect x="18" y="88" width="172" height="24" rx="8" class="stitch-spec-hdr" />
    <text x="28" y="104" class="stitch-text-gold" font-size="9" font-weight="800" letter-spacing="0.5">UPPERWEAR SPEC</text>
    
    <text x="28" y="126" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">PIECE</text>
    <text x="68" y="126" class="stitch-text-title" font-size="9" font-weight="700">{disp_upper[:20]}</text>
    
    <text x="28" y="148" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">FABRIC</text>
    <text x="68" y="148" class="stitch-text-body" font-size="8.5" font-weight="600">{disp_upper_fab[:20]}</text>
    
    <text x="28" y="172" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">TONE</text>
    <circle cx="74" cy="169" r="5" fill="{upper_hex}" stroke="rgba(255,255,255,0.4)" stroke-width="1" />
    <text x="86" y="172" class="stitch-text-title" font-family="'JetBrains Mono', monospace" font-size="8.5" font-weight="600">{upper_hex.upper()}</text>
    
    <!-- Precision Indicator Pointer Arrow (pointing to shirt chest) -->
    <path d="M 190 144 L 236 144" class="stitch-arrow-line" />
    <circle cx="190" cy="144" r="3" class="stitch-arrow-head" />
    <polygon points="236,140 244,144 236,148" class="stitch-arrow-head" />
  </g>

  <!-- B. BOTTOMWEAR SPEC TABLE -->
  <g>
    <rect x="18" y="268" width="172" height="114" rx="8" class="stitch-spec-card" />
    <rect x="18" y="268" width="172" height="24" rx="8" class="stitch-spec-hdr" />
    <text x="28" y="284" class="stitch-text-gold" font-size="9" font-weight="800" letter-spacing="0.5">BOTTOMWEAR SPEC</text>
    
    <text x="28" y="306" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">PIECE</text>
    <text x="68" y="306" class="stitch-text-title" font-size="9" font-weight="700">{disp_bottom[:20]}</text>
    
    <text x="28" y="328" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">FABRIC</text>
    <text x="68" y="328" class="stitch-text-body" font-size="8.5" font-weight="600">{disp_bottom_fab[:20]}</text>
    
    <text x="28" y="352" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">TONE</text>
    <circle cx="74" cy="349" r="5" fill="{bottom_hex}" stroke="rgba(255,255,255,0.4)" stroke-width="1" />
    <text x="86" y="352" class="stitch-text-title" font-family="'JetBrains Mono', monospace" font-size="8.5" font-weight="600">{bottom_hex.upper()}</text>
    
    <!-- Precision Indicator Pointer Arrow (pointing to trousers leg) -->
    <path d="M 190 324 L 244 324" class="stitch-arrow-line" />
    <circle cx="190" cy="324" r="3" class="stitch-arrow-head" />
    <polygon points="244,320 252,324 244,328" class="stitch-arrow-head" />
  </g>

  <!-- C. FOOTWEAR SPEC TABLE -->
  <g>
    <rect x="18" y="440" width="172" height="114" rx="8" class="stitch-spec-card" />
    <rect x="18" y="440" width="172" height="24" rx="8" class="stitch-spec-hdr" />
    <text x="28" y="456" class="stitch-text-gold" font-size="9" font-weight="800" letter-spacing="0.5">FOOTWEAR SPEC</text>
    
    <text x="28" y="478" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">PIECE</text>
    <text x="68" y="478" class="stitch-text-title" font-size="9" font-weight="700">{disp_shoes[:20]}</text>
    
    <text x="28" y="500" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">MATERIAL</text>
    <text x="74" y="500" class="stitch-text-body" font-size="8.5" font-weight="600">{disp_shoes_mat[:18]}</text>
    
    <text x="28" y="524" class="stitch-text-muted" font-size="7.5" font-weight="700" letter-spacing="0.3">TONE</text>
    <circle cx="74" cy="521" r="5" fill="{shoes_hex}" stroke="rgba(255,255,255,0.4)" stroke-width="1" />
    <text x="86" y="524" class="stitch-text-title" font-family="'JetBrains Mono', monospace" font-size="8.5" font-weight="600">{shoes_hex.upper()}</text>
    
    <!-- Precision Indicator Pointer Arrow (pointing to shoes) -->
    <path d="M 190 480 L 236 480" class="stitch-arrow-line" />
    <circle cx="190" cy="480" r="3" class="stitch-arrow-head" />
    <polygon points="236,476 244,480 236,484" class="stitch-arrow-head" />
  </g>


  <!-- ==================== CENTER STUDIO: GARMENTS WITH GENEROUS PHYSICAL SPACING ==================== -->

  <!-- 1. UPPERWEAR SHIRT (y: 88 to 220) -->
  <g filter="url(#softShadow_{look_number})">
    <!-- Tailored Upper Silhouette with Notched Collar & Drape -->
    <path d="M 250 88 L 279 107 L 321 107 L 350 88 L 388 124 L 362 152 L 344 142 L 344 220 L 256 220 L 256 142 L 238 152 L 212 124 Z" 
          fill="url(#upperGrad_{look_number})" stroke="rgba(255,255,255,0.22)" stroke-width="1.2" />
    
    <!-- Lapel / V-Neckfold -->
    <path d="M 279 107 L 300 144 L 321 107 Z" fill="rgba(0,0,0,0.22)" />
    <path d="M 300 107 L 300 144" stroke="rgba(255,255,255,0.25)" stroke-width="1" />
    
    <!-- Sartorial Buttons & Placket -->
    <line x1="300" y1="144" x2="300" y2="220" stroke="rgba(255,255,255,0.22)" stroke-width="1.2" stroke-dasharray="4,2" />
    <circle cx="300" cy="162" r="2.8" fill="url(#goldGrad_{look_number})" />
    <circle cx="300" cy="186" r="2.8" fill="url(#goldGrad_{look_number})" />
    <circle cx="300" cy="210" r="2.8" fill="url(#goldGrad_{look_number})" />
    
    <!-- Pocket Accent Detail -->
    <path d="M 264 172 L 286 172" stroke="rgba(255,255,255,0.22)" stroke-width="1.5" />
  </g>

  <!-- *** GENEROUS PHYSICAL GAP 1: 35px empty breathing room between shirt (y:220) and trousers (y:255) *** -->

  <!-- 2. BOTTOMWEAR TROUSERS (y: 255 to 415) -->
  <g filter="url(#softShadow_{look_number})">
    <!-- Contoured Waistband & Belt Loops -->
    <rect x="254" y="255" width="92" height="15" rx="2" fill="url(#bottomGrad_{look_number})" stroke="rgba(255,255,255,0.2)" stroke-width="1" />
    <line x1="274" y1="255" x2="274" y2="270" stroke="rgba(255,255,255,0.25)" stroke-width="1.2" />
    <line x1="300" y1="255" x2="300" y2="270" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
    <line x1="326" y1="255" x2="326" y2="270" stroke="rgba(255,255,255,0.25)" stroke-width="1.2" />

    <!-- Tailored Trouser Legs -->
    <path d="M 254 270 L 244 415 L 292 415 L 300 315 L 308 415 L 356 415 L 346 270 Z" 
          fill="url(#bottomGrad_{look_number})" stroke="rgba(255,255,255,0.2)" stroke-width="1.2" />

    <!-- Pressed Center Crease Lines -->
    <line x1="268" y1="274" x2="268" y2="410" stroke="rgba(255,255,255,0.18)" stroke-width="1.2" />
    <line x1="332" y1="274" x2="332" y2="410" stroke="rgba(255,255,255,0.18)" stroke-width="1.2" />
    
    <!-- Turn-up Hem Cuffs -->
    <rect x="243" y="407" width="50" height="8" rx="1.5" fill="rgba(0,0,0,0.2)" stroke="rgba(255,255,255,0.15)" />
    <rect x="307" y="407" width="50" height="8" rx="1.5" fill="rgba(0,0,0,0.2)" stroke="rgba(255,255,255,0.15)" />
  </g>

  <!-- *** GENEROUS PHYSICAL GAP 2: 32px empty breathing room between trousers (y:415) and shoes (y:448) *** -->

  <!-- 3. FOOTWEAR ENSEMBLE (Sartorial Loafer/Sneaker Silhouette with 20px Center Separation) -->
  <g filter="url(#softShadow_{look_number})">
    <!-- Soft Contact Shadows Underneath -->
    <ellipse cx="268" cy="508" rx="22" ry="3.5" fill="#000000" fill-opacity="0.45" />
    <ellipse cx="332" cy="508" rx="22" ry="3.5" fill="#000000" fill-opacity="0.45" />

    <!-- === LEFT SHOE (Centered at x = 268 beneath left trouser leg, width: 44px, x: 246 to 290) === -->
    <g id="leftShoe_{look_number}">
      <!-- Outsole Base (Stacked leather/rubber welt) -->
      <path d="M 252 454 C 244 466, 244 488, 252 502 C 258 508, 276 509, 284 502 C 291 494, 287 472, 283 454 C 281 450, 255 450, 252 454 Z" 
            fill="#0C1017" stroke="rgba(255,255,255,0.18)" stroke-width="1.2" />
      
      <!-- Contrast Welt Stitched Edge -->
      <path d="M 251 458 C 245 470, 245 488, 253 501 C 258 506, 275 507, 283 501 C 289 493, 286 474, 282 458 Z" 
            fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="0.8" stroke-dasharray="2,1.5" />
      
      <!-- Upper Leather Body -->
      <path d="M 253 456 C 246 468, 246 488, 254 500 C 259 505, 274 506, 282 500 C 288 492, 285 474, 281 456 C 279 452, 255 452, 253 456 Z" 
            fill="url(#shoeGrad_{look_number})" stroke="rgba(255,255,255,0.32)" stroke-width="1" />
      
      <!-- Stitched Apron / Toe Box Contour -->
      <path d="M 255 488 C 259 496, 277 496, 281 488" 
            fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="1" stroke-dasharray="2.5,1.5" />
      
      <!-- Instep Saddle Strap -->
      <path d="M 248 474 C 267 476, 269 476, 288 474 L 287 482 C 269 484, 267 484, 249 482 Z" 
            fill="url(#shoeGrad_{look_number})" stroke="rgba(255,255,255,0.38)" stroke-width="0.8" />
      <rect x="262" y="476" width="12" height="3.5" rx="1.5" fill="#0C1017" stroke="url(#goldGrad_{look_number})" stroke-width="0.8" />
      
      <!-- Foot Entry Collar & Insole Depth -->
      <ellipse cx="267" cy="462" rx="9" ry="6" fill="#0E121A" stroke="rgba(255,255,255,0.22)" stroke-width="1" />
      <ellipse cx="267" cy="464" rx="6" ry="3.5" fill="#182030" />
      <circle cx="267" cy="459" r="1.6" fill="url(#goldGrad_{look_number})" />
    </g>

    <!-- *** 20px LATERAL SEPARATION GAP: Left shoe ends at x=290, Right shoe starts at x=310 across center guide x=300 *** -->

    <!-- === RIGHT SHOE (Centered at x = 332 beneath right trouser leg, width: 44px, x: 310 to 354) === -->
    <g id="rightShoe_{look_number}">
      <!-- Outsole Base (Stacked leather/rubber welt) -->
      <path d="M 317 454 C 313 472, 309 494, 316 502 C 324 509, 342 508, 348 502 C 356 488, 356 466, 348 454 C 345 450, 319 450, 317 454 Z" 
            fill="#0C1017" stroke="rgba(255,255,255,0.18)" stroke-width="1.2" />
      
      <!-- Contrast Welt Stitched Edge -->
      <path d="M 318 458 C 314 474, 311 493, 317 501 C 325 507, 342 506, 347 501 C 355 488, 355 470, 349 458 Z" 
            fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="0.8" stroke-dasharray="2,1.5" />
      
      <!-- Upper Leather Body -->
      <path d="M 319 456 C 315 474, 312 492, 318 500 C 326 506, 341 505, 346 500 C 354 488, 354 468, 347 456 C 345 452, 321 452, 319 456 Z" 
            fill="url(#shoeGrad_{look_number})" stroke="rgba(255,255,255,0.32)" stroke-width="1" />
      
      <!-- Stitched Apron / Toe Box Contour -->
      <path d="M 319 488 C 323 496, 341 496, 345 488" 
            fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="1" stroke-dasharray="2.5,1.5" />
      
      <!-- Instep Saddle Strap -->
      <path d="M 312 474 C 331 476, 333 476, 352 474 L 351 482 C 333 484, 331 484, 313 482 Z" 
            fill="url(#shoeGrad_{look_number})" stroke="rgba(255,255,255,0.38)" stroke-width="0.8" />
      <rect x="326" y="476" width="12" height="3.5" rx="1.5" fill="#0C1017" stroke="url(#goldGrad_{look_number})" stroke-width="0.8" />
      
      <!-- Foot Entry Collar & Insole Depth -->
      <ellipse cx="333" cy="462" rx="9" ry="6" fill="#0E121A" stroke="rgba(255,255,255,0.22)" stroke-width="1" />
      <ellipse cx="333" cy="464" rx="6" ry="3.5" fill="#182030" />
      <circle cx="333" cy="459" r="1.6" fill="url(#goldGrad_{look_number})" />
    </g>
  </g>


  <!-- ==================== 3. RIGHT STUDIO VAULT: HAUTE JEWELLERY & BEAUTY ==================== -->
  <g>
    <!-- Showcase Vault Panel -->
    <rect x="390" y="88" width="252" height="466" rx="14" class="stitch-vault-panel" />
    <rect x="390" y="88" width="252" height="34" rx="14" class="stitch-header-pill" />
    <rect x="390" y="108" width="252" height="14" class="stitch-header-pill" />
    
    <!-- Vault Badge Header -->
    <text x="404" y="110" class="stitch-text-gold" font-size="10" font-weight="800" letter-spacing="0.8">
      {"HAUTE JEWELLERY & BEAUTY" if is_female else "HAUTE HOROLOGY & JEWELLERY"}
    </text>

    <!-- ITEM 1: RINGS (MALE) OR NECKLACE (FEMALE) -->
    <g transform="translate(402, 134)">
      <rect width="228" height="98" rx="9" class="stitch-item-tray" />
      
      {f'''<!-- Female Necklace Showcase -->
      <path d="M 28 20 C 28 52, 68 52, 68 20" fill="none" stroke="url(#goldGrad_{look_number})" stroke-width="2.5" />
      <path d="M 34 22 C 34 48, 62 48, 62 22" fill="none" stroke="{jewel_hex}" stroke-width="1.5" stroke-dasharray="3,2" />
      <circle cx="48" cy="50" r="5" fill="#FFFFFF" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
      <text x="86" y="32" class="stitch-text-title" font-size="10.5" font-weight="700">Choker / Fine Chain</text>
      <text x="86" y="48" class="stitch-text-gold" font-size="9.5" font-weight="600">{metal_name}</text>
      <text x="86" y="66" class="stitch-text-muted" font-size="8.5">Luminescent Neckline Anchor</text>
      ''' if is_female else f'''<!-- Male Signet Ring Showcase -->
      <circle cx="44" cy="48" r="18" fill="none" stroke="url(#goldGrad_{look_number})" stroke-width="4.5" />
      <rect x="36" y="36" width="16" height="12" rx="2" fill="{jewel_hex}" stroke="#FFF" stroke-width="0.8" />
      <circle cx="44" cy="42" r="2.2" fill="#FFFFFF" />
      <text x="84" y="32" class="stitch-text-title" font-size="10.5" font-weight="700">Artisan Signet Ring</text>
      <text x="84" y="48" class="stitch-text-gold" font-size="9.5" font-weight="600">{metal_name}</text>
      <text x="84" y="66" class="stitch-text-muted" font-size="8.5">Hammered Edge / Signet Band</text>
      '''}
    </g>

    <!-- ITEM 2: EARRINGS (MALE: HUGGIE / OBSIDIAN; FEMALE: DROP PEARL) -->
    <g transform="translate(402, 244)">
      <rect width="228" height="98" rx="9" class="stitch-item-tray" />
      
      {f'''<!-- Female Sculptural Drop Earrings -->
      <circle cx="36" cy="30" r="3" fill="url(#goldGrad_{look_number})" />
      <line x1="36" y1="33" x2="36" y2="52" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
      <circle cx="36" cy="58" r="6.5" fill="#FFFFFF" stroke="{jewel_hex}" stroke-width="1.2" />
      
      <circle cx="56" cy="30" r="3" fill="url(#goldGrad_{look_number})" />
      <line x1="56" y1="33" x2="56" y2="52" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
      <circle cx="56" cy="58" r="6.5" fill="#FFFFFF" stroke="{jewel_hex}" stroke-width="1.2" />

      <text x="84" y="32" class="stitch-text-title" font-size="10.5" font-weight="700">Sculptural Drops</text>
      <text x="84" y="48" class="stitch-text-gold" font-size="9.5" font-weight="600">Freshwater Pearl &amp; Gold</text>
      <text x="84" y="66" class="stitch-text-muted" font-size="8.5">Face-Framing Dermal Radiance</text>
      ''' if is_female else f'''<!-- Male Minimalist Huggie Earring -->
      <circle cx="36" cy="48" r="11" fill="none" stroke="url(#goldGrad_{look_number})" stroke-width="2.8" stroke-dasharray="16,4" />
      <circle cx="56" cy="48" r="11" fill="none" stroke="#222" stroke-width="3" />
      <circle cx="56" cy="48" r="9" fill="#0A0A0A" />

      <text x="84" y="32" class="stitch-text-title" font-size="10.5" font-weight="700">Minimalist Huggies</text>
      <text x="84" y="48" class="stitch-text-gold" font-size="9.5" font-weight="600">Titanium &amp; Black Obsidian</text>
      <text x="84" y="66" class="stitch-text-muted" font-size="8.5">Understated Ear Profile</text>
      '''}
    </g>

    <!-- ITEM 3: LIPSTICK TINT (FEMALE) OR LUXURY HOROLOGY (MALE) -->
    <g transform="translate(402, 354)">
      <rect width="228" height="184" rx="9" class="stitch-item-tray" />
      
      {f'''<!-- Female Luxury Lip Tint Showcase -->
      <g transform="translate(24, 24)">
        <rect x="0" y="24" width="22" height="50" rx="4" fill="url(#lipGrad_{look_number})" stroke="rgba(255,255,255,0.3)" stroke-width="1.2" />
        <rect x="2" y="2" width="18" height="24" rx="2" fill="#0C0E14" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
        <line x1="2" y1="12" x2="20" y2="12" stroke="url(#goldGrad_{look_number})" stroke-width="1" />
        <ellipse cx="44" cy="50" rx="14" ry="7.5" fill="{lipstick_hex}" stroke="#FFFFFF" stroke-width="1.2" />
      </g>
      <text x="80" y="34" class="stitch-text-title" font-size="10.5" font-weight="700">Signature Lip Tint</text>
      <text x="80" y="52" fill="{lipstick_hex}" font-family="'Plus Jakarta Sans', system-ui" font-size="10" font-weight="700">{disp_lip[:20]}</text>
      <text x="80" y="70" class="stitch-text-gold" font-size="9" font-weight="600">{lipstick_finish}</text>
      <rect x="80" y="94" width="138" height="24" rx="5" class="stitch-header-pill" />
      <text x="86" y="110" fill="#34D399" font-family="'Plus Jakarta Sans', system-ui" font-size="8.5" font-weight="700">✓ Dermal Undertone Match</text>
      ''' if is_female else f'''<!-- Male Chronograph Horology Showcase -->
      <g transform="translate(20, 24)">
        <rect x="18" y="2" width="18" height="82" rx="2" fill="{shoes_hex}" stroke="#000" stroke-width="1" />
        <circle cx="27" cy="42" r="22" fill="#0D111A" stroke="url(#goldGrad_{look_number})" stroke-width="3" />
        <circle cx="27" cy="42" r="17" fill="#141B26" />
        <circle cx="27" cy="35" r="3.5" fill="none" stroke="#F2CA50" stroke-width="0.8" />
        <line x1="27" y1="42" x2="27" y2="30" stroke="#FFFFFF" stroke-width="1.5" />
        <line x1="27" y1="42" x2="36" y2="42" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
      </g>
      <text x="76" y="34" class="stitch-text-title" font-size="10.5" font-weight="700">Chronograph Watch</text>
      <text x="76" y="52" class="stitch-text-gold" font-size="10" font-weight="700">{disp_lip[:20]}</text>
      <text x="76" y="70" class="stitch-text-muted" font-size="9" font-weight="600">Bezel: {metal_name}</text>
      <rect x="76" y="94" width="142" height="24" rx="5" class="stitch-header-pill" />
      <text x="82" y="110" fill="#34D399" font-family="'Plus Jakarta Sans', system-ui" font-size="8.5" font-weight="700">✓ Horology In Harmony</text>
      '''}
    </g>
  </g>


  <!-- ==================== 4. BOTTOM ATELIER HARMONY BAR & CERTIFICATE ==================== -->
  <g transform="translate(18, 568)">
    <rect width="624" height="254" rx="14" class="stitch-formula-panel" />
    
    <!-- Title and Harmony Percentage -->
    <text x="24" y="34" class="stitch-text-gold" font-size="13" font-weight="700" letter-spacing="0.5">ATELIER CHROMATIC FORMULA</text>
    <rect x="472" y="16" width="128" height="26" rx="13" fill="rgba(52, 211, 153, 0.15)" stroke="#34D399" stroke-width="1.2" />
    <text x="488" y="33" fill="#34D399" font-family="'Plus Jakarta Sans', system-ui" font-size="10" font-weight="800">★ 96.8% HARMONY</text>

    <!-- 4 Structured Formula Spec Cards (Spaced with 144px width each) -->
    <!-- Column 1: Upperwear -->
    <g transform="translate(20, 56)">
      <rect width="136" height="106" rx="8" class="stitch-item-tray" />
      <circle cx="26" cy="28" r="14" fill="{upper_hex}" stroke="#FFF" stroke-opacity="0.3" stroke-width="1.5" />
      <text x="48" y="24" class="stitch-text-title" font-size="10" font-weight="700">Upperwear</text>
      <text x="48" y="38" class="stitch-text-muted" font-family="'JetBrains Mono', monospace" font-size="8.5">{upper_hex.upper()}</text>
      <text x="14" y="64" class="stitch-text-body" font-size="8.5" font-weight="600">{disp_upper[:20]}</text>
      <text x="14" y="82" class="stitch-text-muted" font-size="8">{disp_upper_fab[:20]}</text>
    </g>

    <!-- Column 2: Bottomwear -->
    <g transform="translate(168, 56)">
      <rect width="136" height="106" rx="8" class="stitch-item-tray" />
      <circle cx="26" cy="28" r="14" fill="{bottom_hex}" stroke="#FFF" stroke-opacity="0.3" stroke-width="1.5" />
      <text x="48" y="24" class="stitch-text-title" font-size="10" font-weight="700">Bottomwear</text>
      <text x="48" y="38" class="stitch-text-muted" font-family="'JetBrains Mono', monospace" font-size="8.5">{bottom_hex.upper()}</text>
      <text x="14" y="64" class="stitch-text-body" font-size="8.5" font-weight="600">{disp_bottom[:20]}</text>
      <text x="14" y="82" class="stitch-text-muted" font-size="8">{disp_bottom_fab[:20]}</text>
    </g>

    <!-- Column 3: Footwear -->
    <g transform="translate(316, 56)">
      <rect width="136" height="106" rx="8" class="stitch-item-tray" />
      <circle cx="26" cy="28" r="14" fill="{shoes_hex}" stroke="#FFF" stroke-opacity="0.3" stroke-width="1.5" />
      <text x="48" y="24" class="stitch-text-title" font-size="10" font-weight="700">Footwear</text>
      <text x="48" y="38" class="stitch-text-muted" font-family="'JetBrains Mono', monospace" font-size="8.5">{shoes_hex.upper()}</text>
      <text x="14" y="64" class="stitch-text-body" font-size="8.5" font-weight="600">{disp_shoes[:20]}</text>
      <text x="14" y="82" class="stitch-text-muted" font-size="8">{disp_shoes_mat[:20]}</text>
    </g>

    <!-- Column 4: Accent & Jewellery -->
    <g transform="translate(464, 56)">
      <rect width="140" height="106" rx="8" class="stitch-item-tray" />
      <circle cx="26" cy="28" r="14" fill="{jewel_hex}" stroke="url(#goldGrad_{look_number})" stroke-width="1.5" />
      <text x="48" y="24" class="stitch-text-title" font-size="9.5" font-weight="700">{"Jewellery/Lip" if is_female else "Jewellery/Dial"}</text>
      <text x="48" y="38" class="stitch-text-gold" font-family="'JetBrains Mono', monospace" font-size="8.5">{jewel_hex.upper()}</text>
      <text x="14" y="64" class="stitch-text-body" font-size="8.5" font-weight="600">{metal_name[:18]}</text>
      <text x="14" y="82" class="stitch-text-muted" font-size="8">{"Dermal Luster Accent" if is_female else "Horology Finish"}</text>
    </g>

    <!-- Subtle Certification Watermark -->
    <line x1="20" y1="186" x2="604" y2="186" class="stitch-divider" />
    <text x="24" y="214" class="stitch-watermark" font-size="9" font-weight="600" letter-spacing="0.5">
      CALIBRATED BY OTTERLOOK AI • HAUTE COUTURE COLORIMETRY ATELIER
    </text>
    <text x="496" y="214" class="stitch-text-gold" font-size="9.5" font-weight="700">
      ★ CERTIFIED LOOK
    </text>
  </g>
</svg>"""
    return svg
