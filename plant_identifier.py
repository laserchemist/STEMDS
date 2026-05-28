"""
plant_identifier.py
===================
Helper tools for the Plant Explorer notebook.

Uses CLIP (Contrastive Language-Image Pretraining) to compare plant photos
by measuring how close their image embeddings are in vector space.
No API key required — everything runs locally.

How CLIP similarity works
--------------------------
CLIP converts every image into a list of ~512 numbers called an *embedding*
(think of it as a GPS address in a 512-dimensional space). Similar-looking
images end up at nearby addresses. We measure similarity using *cosine
similarity* — the cosine of the angle between two embedding vectors:
  • cos θ = 1.0  →  vectors point the same direction  → identical images
  • cos θ = 0.7  →  vectors point at ~46° apart       → quite different

Raw CLIP cosine values sit between ~0.6 and 1.0 for natural photos.
We rescale them so 0.6 → 0 % and 1.0 → 100 % for easier reading.

Middle School Plant Science Project
"""

import os
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS



def _path(plant_dict):
    """Accept either 'path' or 'plants' as the image-path key.
    Searches common subdirectories automatically when the bare filename is missing."""
    raw = plant_dict.get("path") or plant_dict.get("plants") or ""
    if not raw:
        return ""
    if os.path.isfile(raw):
        return raw
    # Try common subdirectory names
    for folder in ("plants", "images", "photos", "img"):
        candidate = os.path.join(folder, raw)
        if os.path.isfile(candidate):
            return candidate
    return raw   # return as-is so the error message shows the attempted path


# ── File checker ───────────────────────────────────────────────────────────────

def check_photos(unknown_path, known_plants):
    """
    Verify every photo file exists AND is a valid image.
    Prints a clear ✅ / ❌ / ⚠️ list so students know exactly what to fix.
    """
    import glob as _glob
    all_ok = True
    all_photos = [("Mystery Plant", unknown_path)] + \
                 [(p["name"], _path(p)) for p in known_plants]

    print("Checking photo files...\n")
    for name, path in all_photos:
        if not os.path.isfile(path):
            print(f"  ❌  {name:20s}  →  \'{path}\' NOT FOUND")
            filename = os.path.basename(path)
            matches = _glob.glob(f"**/{filename}", recursive=True)
            if matches:
                print(f"       Did you mean: {matches[0]}  — update the path in Step 1.")
            else:
                print(f"       Upload this file, then update the path in Step 1.")
                print(f"       If it\'s in a subfolder write:  \"path\": \"plants/{filename}\"")
            all_ok = False
            continue

        size_kb = os.path.getsize(path) // 1024
        try:
            with Image.open(path) as img:
                img.verify()
            print(f"  ✅  {name:20s}  →  {path}  ({size_kb} KB)")
        except Exception:
            print(f"  ⚠️   {name:20s}  →  {path}  ({size_kb} KB)  ← NOT a valid image!")
            print(f"       The file exists but cannot be read as a photo.")
            print(f"       It may have downloaded as an HTML page instead of an image.")
            print(f"       Right-click the image in your browser → Save image as...")
            all_ok = False

    if all_ok:
        print("\n✅ All photos valid — ready to continue!")
    else:
        print("\n⚠️  Fix the issues above, then re-run the Step 1 cell.")
    return all_ok


# ── CLIP model (loaded once, cached) ──────────────────────────────────────────
_model     = None
_processor = None

def load_clip(model_name="openai/clip-vit-base-patch32"):
    """
    Download (first time only) and cache the CLIP model.
    After the first run the model is saved locally and loads instantly.
    """
    global _model, _processor
    if _model is None:
        from transformers import CLIPModel, CLIPProcessor
        print(f"Loading CLIP model ({model_name})…")
        print("First run: downloads ~600 MB — this takes a minute or two.")
        print("Subsequent runs: loads from cache in a few seconds.\n")
        _processor = CLIPProcessor.from_pretrained(model_name)
        # use_safetensors=True avoids the torch.load path that requires torch ≥ 2.6
        _model     = CLIPModel.from_pretrained(model_name, use_safetensors=True).eval()
        print("✅ CLIP model ready!\n")
    return _model, _processor


# ── Image embedding ────────────────────────────────────────────────────────────

def get_embedding(image_path):
    """
    Convert a plant photo into a 512-number embedding vector using CLIP.

    Parameters
    ----------
    image_path : str
        Path to the image file.

    Returns
    -------
    torch.Tensor  shape (1, 512), L2-normalised (unit vector)
    """
    model, processor = load_clip()
    img    = Image.open(image_path).convert("RGB")
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        # get_image_features() now returns a BaseModelOutputWithPooling object
        # (not a plain tensor) — the projected embedding lives in .pooler_output
        output   = model.get_image_features(pixel_values=inputs["pixel_values"])
        features = output.pooler_output
    return F.normalize(features, dim=-1)   # unit vector → cosine sim = dot product


def _rescale(cosine_val, low=0.60):
    """
    Rescale a raw CLIP cosine similarity to a 0–1 display score.

    Raw CLIP similarities for real photos are roughly 0.60–1.00.
    We map [low, 1.0] → [0.0, 1.0] so students see intuitive percentages.
    """
    return float(max(0.0, (cosine_val - low) / (1.0 - low)))


# ── Image display utilities ────────────────────────────────────────────────────

def show_image(path, title=""):
    """Display a single plant photo inside the notebook."""
    img = Image.open(path)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(img)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=10)
    plt.tight_layout()
    plt.show()


def show_all_plants(unknown_path, known_plants):
    """
    Display the mystery plant and all known plants side by side.

    Parameters
    ----------
    unknown_path : str
        Path to the mystery plant photo.
    known_plants : list of dict
        Each dict must have 'name' and 'path' keys.
    """
    n = len(known_plants) + 1
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    def _safe_open(path):
        try:
            return Image.open(path).convert("RGB")
        except Exception:
            return None

    def _render(ax, img, title, color):
        if img:
            ax.imshow(img)
        else:
            ax.text(0.5, 0.5,
                    "Cannot open file.\nRe-download as a\nproper .jpg or .png.",
                    ha="center", va="center", fontsize=10,
                    color="#cc3333", transform=ax.transAxes)
            ax.set_facecolor("#fff0f0")
        ax.set_title(title, fontsize=13, fontweight="bold", color=color)
        ax.axis("off")

    _render(axes[0], _safe_open(unknown_path), "Mystery Plant", "#333333")

    for i, plant in enumerate(known_plants):
        _render(axes[i + 1], _safe_open(_path(plant)), plant['name'], "#2d6a2d")

    plt.suptitle("Plant Photo Comparison", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.show()


# ── GPS / location utilities ───────────────────────────────────────────────────

def extract_gps(image_path):
    """
    Try to read GPS coordinates stored inside a photo's EXIF data.

    Returns a dict with 'latitude' and 'longitude', or None if not found.
    """
    try:
        img      = Image.open(image_path)
        exif_raw = img._getexif()
        if not exif_raw:
            return None

        gps_info = {}
        for tag_id, value in exif_raw.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_id, gps_val in value.items():
                    gps_info[GPSTAGS.get(gps_id, gps_id)] = gps_val

        if "GPSLatitude" not in gps_info:
            return None

        def dms_to_decimal(dms, ref):
            d, m, s = float(dms[0]), float(dms[1]), float(dms[2])
            dec = d + m / 60 + s / 3600
            return -dec if ref in ("S", "W") else dec

        lat = dms_to_decimal(gps_info["GPSLatitude"],  gps_info["GPSLatitudeRef"])
        lon = dms_to_decimal(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
        return {"latitude": round(lat, 6), "longitude": round(lon, 6)}

    except Exception:
        return None


# ── Main comparison function ───────────────────────────────────────────────────

def compare_plants(unknown_path, known_plants):
    """
    Compare the mystery plant to each known plant using CLIP embeddings.

    Steps
    -----
    1. Convert every image to a 512-dimensional embedding vector.
    2. Compute the cosine similarity between the mystery plant vector
       and each known plant vector.
    3. Rescale to a 0–100 % display score and rank the results.

    Parameters
    ----------
    unknown_path : str
        File path to the mystery plant photo.
    known_plants : list of dict
        Each dict must have 'name' (str) and 'path' (str) keys.

    Returns
    -------
    dict
        Keys: similarities (list), best_match (str), best_score (float)
    """
    print("Computing CLIP embedding for mystery plant…")
    unknown_emb = get_embedding(unknown_path)

    similarities = []
    for plant in known_plants:
        print(f"  Comparing with {plant['name']}…")
        known_emb    = get_embedding(_path(plant))
        raw_cosine   = (unknown_emb @ known_emb.T).item()
        display_score = _rescale(raw_cosine)

        similarities.append({
            "name":        plant["name"],
            "probability": round(display_score, 3),   # 0–1 display score
            "raw_cosine":  round(raw_cosine, 4),       # raw CLIP value
        })

    similarities.sort(key=lambda x: x["probability"], reverse=True)
    best = similarities[0]

    print(f"\n✅ Done! Closest match: {best['name']} "
          f"({best['probability']*100:.0f}% similar)")

    return {
        "similarities": similarities,
        "best_match":   best["name"],
        "best_score":   best["probability"],
    }


# ── Embedding visualisation ────────────────────────────────────────────────────

def plot_embeddings(unknown_path, known_plants):
    """
    Project all plant embeddings to 2D using PCA and plot them.

    Points close together on the plot are visually similar according to CLIP.
    This gives students an intuition for what 'embedding space' means.
    """
    from sklearn.decomposition import PCA

    paths = [unknown_path] + [_path(p) for p in known_plants]
    names = ["Mystery Plant"] + [p["name"] for p in known_plants]
    embs  = [get_embedding(p).squeeze().numpy() for p in paths]

    pca    = PCA(n_components=2)
    coords = pca.fit_transform(np.array(embs))

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#cc3333"] + ["#2d6a2d"] * len(known_plants)
    sizes  = [180]        + [120]       * len(known_plants)

    for (x, y), name, color, size in zip(coords, names, colors, sizes):
        ax.scatter(x, y, color=color, s=size, zorder=3, edgecolors="white", linewidths=1.5)
        ax.annotate(name, (x, y), textcoords="offset points",
                    xytext=(8, 4), fontsize=11,
                    color="#333333" if name != "Mystery Plant" else "#cc3333",
                    fontweight="bold" if name == "Mystery Plant" else "normal")

    legend_items = [
        mpatches.Patch(color="#cc3333", label="Mystery plant"),
        mpatches.Patch(color="#2d6a2d", label="Known plants"),
    ]
    ax.legend(handles=legend_items, fontsize=10)
    ax.set_title("Plant embeddings projected to 2D (PCA)\n"
                 "Closer points = more similar according to CLIP",
                 fontsize=12, fontweight="bold")
    ax.set_xlabel(f"PCA axis 1  ({pca.explained_variance_ratio_[0]*100:.0f}% of variation)")
    ax.set_ylabel(f"PCA axis 2  ({pca.explained_variance_ratio_[1]*100:.0f}% of variation)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()


# ── Results bar chart ──────────────────────────────────────────────────────────

def plot_results(result):
    """
    Display a colour-coded bar chart of similarity scores.

    Parameters
    ----------
    result : dict
        The dict returned by compare_plants().
    """
    similarities = result["similarities"]
    names  = [s["name"]        for s in similarities]
    scores = [s["probability"] for s in similarities]

    colors = ["#2d6a2d" if p >= 0.55 else "#e8a020" if p >= 0.25 else "#cc3333"
              for p in scores]

    fig, ax = plt.subplots(figsize=(8, max(3, len(names) * 1.3)))
    bars = ax.barh(names, scores, color=colors, edgecolor="white", height=0.55)

    for bar, p in zip(bars, scores):
        ax.text(min(p + 0.02, 1.05), bar.get_y() + bar.get_height() / 2,
                f"{p * 100:.0f}%", va="center", fontsize=12,
                fontweight="bold", color="#333333")

    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Visual similarity score  (0 = completely different, 100 % = identical)",
                  fontsize=11)
    ax.set_title(
        f"How similar is each known plant to the mystery plant?\n"
        f"Closest match: {result['best_match']}  "
        f"({result['best_score']*100:.0f}%)",
        fontsize=13, fontweight="bold", pad=12)

    legend_items = [
        mpatches.Patch(color="#2d6a2d", label="High similarity  ≥ 55%"),
        mpatches.Patch(color="#e8a020", label="Medium similarity  25–54%"),
        mpatches.Patch(color="#cc3333", label="Low similarity  < 25%"),
    ]
    ax.legend(handles=legend_items, loc="lower right", fontsize=10)
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Text summary
    print("\n📋 Similarity scores (raw cosine values):")
    for s in similarities:
        filled = "█" * int(s["probability"] * 20)
        empty  = "░" * (20 - int(s["probability"] * 20))
        print(f"  {s['name']:25s} [{filled}{empty}] "
              f"{s['probability']*100:.0f}%  (cosine = {s['raw_cosine']:.3f})")


# ── Interactive map ────────────────────────────────────────────────────────────

def make_map(plant_locations, zoom_start=15):
    """
    Create an interactive map showing where each plant was found.

    Parameters
    ----------
    plant_locations : list of dict
        Each dict: {'name': str, 'latitude': float, 'longitude': float,
                    'note': str (optional)}

    Returns
    -------
    folium.Map  (displays automatically in Jupyter)
    """
    try:
        import folium
    except ImportError:
        print("❌ folium not installed. Run:  pip install folium  then restart.")
        return None

    if not plant_locations:
        print("⚠️  No plant locations to map.")
        return None

    lats   = [p["latitude"]  for p in plant_locations]
    lons   = [p["longitude"] for p in plant_locations]
    center = [sum(lats) / len(lats), sum(lons) / len(lons)]

    m = folium.Map(location=center, zoom_start=zoom_start, tiles="OpenStreetMap")

    colors = ["green", "blue", "red", "purple", "orange",
              "darkgreen", "cadetblue", "darkred"]

    for i, plant in enumerate(plant_locations):
        popup_html = (
            f"<div style='font-family:sans-serif;font-size:13px;min-width:150px'>"
            f"<b>🌿 {plant['name']}</b><br>"
            f"<span style='color:#555'>📍 {plant['latitude']:.5f}, "
            f"{plant['longitude']:.5f}</span>"
            + (f"<br><i>{plant.get('note','')}</i>" if plant.get("note") else "")
            + "</div>"
        )
        folium.Marker(
            location=[plant["latitude"], plant["longitude"]],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"🌿 {plant['name']}",
            icon=folium.Icon(color=colors[i % len(colors)], icon="leaf", prefix="fa")
        ).add_to(m)

    return m
