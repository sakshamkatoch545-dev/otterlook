"""
Colorimetric Dataset Generator for Facial Skin Undertone Analysis.
Generates a structured, scientifically-grounded dataset based on dermatological
and colorimetric principles (CIELAB L*a*b*, HSV, and sRGB color spaces across
Fitzpatrick Skin Phototypes I through VI).

Author: AI Personal Colour Analysis System
"""

import os
import numpy as np
import pandas as pd

def generate_skin_undertone_dataset(num_samples_per_class: int = 400, random_seed: int = 42) -> pd.DataFrame:
    """
    Synthesizes a realistic dataset of multi-region facial skin color features.
    
    Physics & Color Science Rationale:
    - Warm Undertone: Dominated by carotenoids & pheomelanin, leading to higher CIELAB b* (yellow),
      moderately high RGB G and R, HSV Hue centered in the golden/peach band (20-40°).
    - Cool Undertone: Dominated by cutaneous hemoglobin & lower yellow balance, leading to
      lower CIELAB b* (cooler blue-leaning), elevated a* (pink/rose), HSV Hue in red/pink band (5-18°).
    - Neutral Undertone: Balanced yellow and pink components without extreme saturation,
      intermediate b* (12-18) and a* (10-17).
      
    Covers diverse Fitzpatrick Phototypes (Light, Medium, Tan, Deep/Dark):
    - Light/Fair: L* in [68, 88]
    - Medium/Olive: L* in [52, 70]
    - Tan/Deep: L* in [38, 55]
    - Dark/Rich: L* in [22, 42]
    """
    np.random.seed(random_seed)
    records = []
    
    undertones = ["Warm", "Cool", "Neutral"]
    phototypes = ["Fair", "Medium", "Tan", "Deep"]
    
    sample_id = 1
    
    for undertone in undertones:
        for _ in range(num_samples_per_class):
            phototype = np.random.choice(phototypes, p=[0.30, 0.35, 0.20, 0.15])
            
            # Base Lightness (L*) per phototype
            if phototype == "Fair":
                mean_l = np.random.normal(loc=76.0, scale=4.5)
            elif phototype == "Medium":
                mean_l = np.random.normal(loc=61.0, scale=4.0)
            elif phototype == "Tan":
                mean_l = np.random.normal(loc=48.0, scale=4.0)
            else: # Deep
                mean_l = np.random.normal(loc=33.0, scale=4.5)
            
            mean_l = np.clip(mean_l, 18.0, 92.0)
            
            # CIELAB a* (Red-Green axis) and b* (Yellow-Blue axis) based on undertone
            if undertone == "Warm":
                mean_a = np.random.normal(loc=13.5, scale=2.2)
                # Warm has higher b* (yellower/golden) relative to L*
                base_b = 19.5 + (mean_l - 50) * 0.08
                mean_lab_b = np.random.normal(loc=base_b, scale=2.5)
                # HSV Hue (0-180 scale in OpenCV where 180=360deg, so 10-22 corresponds to 20-44deg golden peach)
                mean_h = np.random.normal(loc=16.0, scale=2.2) # ~32 deg
                mean_s = np.random.normal(loc=95.0, scale=18.0)
            elif undertone == "Cool":
                # Cool has higher a* (pinker/rosier) and lower b* (less yellow, more blue-gray)
                mean_a = np.random.normal(loc=17.2, scale=2.5)
                base_b = 11.0 + (mean_l - 50) * 0.06
                mean_lab_b = np.random.normal(loc=base_b, scale=2.3)
                # HSV Hue closer to red/pink (0-12 in OpenCV corresponds to 0-24deg)
                mean_h = np.random.normal(loc=8.0, scale=2.5)
                mean_s = np.random.normal(loc=80.0, scale=16.0)
            else: # Neutral
                # Neutral has balanced a* and b*
                mean_a = np.random.normal(loc=14.8, scale=2.0)
                base_b = 15.2 + (mean_l - 50) * 0.07
                mean_lab_b = np.random.normal(loc=base_b, scale=2.0)
                mean_h = np.random.normal(loc=12.0, scale=2.0)
                mean_s = np.random.normal(loc=86.0, scale=15.0)
            
            mean_lab_b = np.clip(mean_lab_b, 4.0, 36.0)
            mean_a = np.clip(mean_a, 5.0, 30.0)
            mean_h = np.clip(mean_h, 0.0, 35.0)
            mean_s = np.clip(mean_s, 25.0, 180.0)
            mean_v = np.clip(mean_l * 2.55, 30.0, 250.0)
            
            # Approximate RGB from L*a*b*
            # R is strongly correlated with L* and a*
            r = mean_l * 2.5 + mean_a * 1.8 + np.random.normal(0, 3)
            # G is correlated with L* and influenced negatively by a* and positively by b*
            g = mean_l * 2.2 - mean_a * 0.7 + mean_lab_b * 0.9 + np.random.normal(0, 3)
            # B is correlated with L* and reduced significantly when b* is high
            b = mean_l * 2.1 - mean_lab_b * 1.6 + np.random.normal(0, 3)
            
            mean_r = float(np.clip(r, 20.0, 255.0))
            mean_g = float(np.clip(g, 15.0, 245.0))
            mean_b = float(np.clip(b, 10.0, 235.0))
            
            # Derived color science metrics
            # Individual Typology Angle (ITA) = arctan((L* - 50) / b*) * 180 / pi
            safe_b = max(mean_lab_b, 0.1)
            ita = float(np.arctan((mean_l - 50.0) / safe_b) * 180.0 / np.pi)
            
            # Additional statistical moments (variances, std across sampled regions)
            std_r = float(np.random.uniform(4.0, 12.0))
            std_g = float(np.random.uniform(3.5, 10.5))
            std_b = float(np.random.uniform(3.5, 11.0))
            std_l = float(np.random.uniform(2.0, 6.0))
            std_a = float(np.random.uniform(1.2, 3.5))
            std_b_val = float(np.random.uniform(1.2, 3.8))
            
            median_r = float(mean_r + np.random.normal(0, 1.2))
            median_g = float(mean_g + np.random.normal(0, 1.2))
            median_b = float(mean_b + np.random.normal(0, 1.2))
            
            # Ratio of yellow-to-red in CIELAB (b*/a*)
            b_to_a_ratio = float(mean_lab_b / max(mean_a, 0.1))
            
            # Red-to-Green & Red-to-Blue ratios in RGB
            rg_ratio = float(mean_r / max(mean_g, 1.0))
            rb_ratio = float(mean_r / max(mean_b, 1.0))
            
            records.append({
                "image_id": f"IMG_{sample_id:05d}",
                "phototype": phototype,
                "mean_r": round(mean_r, 3),
                "mean_g": round(mean_g, 3),
                "mean_b": round(mean_b, 3),
                "median_r": round(median_r, 3),
                "median_g": round(median_g, 3),
                "median_b": round(median_b, 3),
                "std_r": round(std_r, 3),
                "std_g": round(std_g, 3),
                "std_b": round(std_b, 3),
                "mean_h": round(mean_h, 3),
                "mean_s": round(mean_s, 3),
                "mean_v": round(mean_v, 3),
                "mean_l": round(mean_l, 3),
                "mean_a": round(mean_a, 3),
                "mean_lab_b": round(mean_lab_b, 3),
                "std_l": round(std_l, 3),
                "std_a": round(std_a, 3),
                "std_lab_b": round(std_b_val, 3),
                "ita": round(ita, 3),
                "b_to_a_ratio": round(b_to_a_ratio, 4),
                "rg_ratio": round(rg_ratio, 4),
                "rb_ratio": round(rb_ratio, 4),
                "undertone": undertone
            })
            sample_id += 1
            
    df = pd.DataFrame(records)
    # Shuffle
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    return df

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "training.csv")
    df = generate_skin_undertone_dataset(num_samples_per_class=450, random_seed=42)
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} samples saved to {csv_path}")
    print(df["undertone"].value_counts())
