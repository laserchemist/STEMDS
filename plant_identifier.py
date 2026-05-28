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
        import logging, transformers as _tf
        from transformers import CLIPModel, CLIPProcessor
        # Silence the verbose transformers download/config messages
        _tf.logging.set_verbosity_error()
        logging.getLogger("transformers").setLevel(logging.ERROR)
        print(f"Loading CLIP model ({model_name})…")
        print("First run: ~600 MB download — takes a minute. Cached after that.\n")
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


# ── Color analysis (high school version) ──────────────────────────────────────

def color_histogram(image_path, bins=64):
    """
    Extract normalised R, G, B intensity histograms from an image.

    Returns
    -------
    dict  {'Red': array, 'Green': array, 'Blue': array, 'edges': array}
    """
    img = np.array(Image.open(image_path).convert("RGB"))
    edges = np.linspace(0, 255, bins + 1)
    result = {"edges": edges}
    for i, ch in enumerate(["Red", "Green", "Blue"]):
        h, _ = np.histogram(img[:, :, i].ravel(), bins=edges)
        result[ch] = h / h.sum()
    return result


def hue_histogram(image_path, bins=36):
    """
    Extract a hue distribution from HSV colour space, ignoring near-grey pixels.
    Returns (hue_centres_degrees, normalised_counts).
    """
    import colorsys
    img = np.array(Image.open(image_path).convert("RGB")) / 255.0
    pixels = img.reshape(-1, 3)
    hues = []
    for r, g, b in pixels:
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        if s > 0.15 and v > 0.15:       # skip near-grey / very dark pixels
            hues.append(h * 360)
    if not hues:
        return np.linspace(5, 355, bins), np.zeros(bins)
    counts, edges = np.histogram(hues, bins=bins, range=(0, 360))
    centres = 0.5 * (edges[:-1] + edges[1:])
    total   = counts.sum()
    return centres, counts / total if total else counts


def dominant_colors(image_path, n_colors=6, sample=4000):
    """
    Find the N most common colours using k-means clustering.

    Returns
    -------
    list of (proportion, [R, G, B]) sorted by proportion descending
    """
    from sklearn.cluster import KMeans
    img    = np.array(Image.open(image_path).convert("RGB"))
    pixels = img.reshape(-1, 3)
    idx    = np.random.choice(len(pixels), min(sample, len(pixels)), replace=False)
    km     = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    km.fit(pixels[idx])
    centres = km.cluster_centers_.astype(int).clip(0, 255)
    labels  = km.labels_
    props   = np.bincount(labels, minlength=n_colors) / len(labels)
    return sorted(zip(props.tolist(), centres.tolist()), reverse=True)


def color_similarity(path1, path2, bins=64):
    """
    Compute colour similarity using histogram intersection.
    Combines R, G, B channels into one normalised histogram vector,
    then takes the intersection (area of overlap).

    Returns
    -------
    float  0.0 (no overlap) to 1.0 (identical distributions)
    """
    def _hist(p):
        img = np.array(Image.open(p).convert("RGB"))
        edges = np.linspace(0, 255, bins + 1)
        parts = []
        for i in range(3):
            h, _ = np.histogram(img[:, :, i].ravel(), bins=edges)
            parts.append(h / h.sum())
        return np.concatenate(parts)

    h1, h2 = _hist(path1), _hist(path2)
    return float(np.minimum(h1, h2).sum() / 3)



# ── Visible-light pseudo-spectrum (400–780 nm) ────────────────────────────────

def _wavelength_to_rgb(wl):
    """
    Convert a wavelength in nm to an approximate sRGB colour (Bruton's algorithm).
    Returns (r, g, b) floats in [0, 1].
    """
    if   380 <= wl < 440: r, g, b = -(wl - 440) / 60,       0.0,             1.0
    elif 440 <= wl < 490: r, g, b =  0.0,          (wl - 440) / 50,           1.0
    elif 490 <= wl < 510: r, g, b =  0.0,          1.0,             -(wl - 510) / 20
    elif 510 <= wl < 580: r, g, b = (wl - 510) / 70,         1.0,             0.0
    elif 580 <= wl < 645: r, g, b =  1.0,          -(wl - 645) / 65,          0.0
    elif 645 <= wl <= 780: r, g, b = 1.0,           0.0,             0.0
    else:                  r, g, b = 0.0,            0.0,             0.0
    # Intensity falloff at UV and deep-red edges
    if   380 <= wl < 420: factor = 0.3 + 0.7 * (wl - 380) / 40
    elif 700 < wl <= 780:  factor = 0.3 + 0.7 * (780 - wl) / 80
    else:                  factor = 1.0
    return (min(1, max(0, r * factor)),
            min(1, max(0, g * factor)),
            min(1, max(0, b * factor)))


def plot_visible_spectra(unknown_path, known_plants):
    """
    Plot an approximate visible-light pseudo-spectrum (400–780 nm) for each plant.

    Method
    ------
    The mean intensity of each colour channel (R, G, B) is used to weight a
    Gaussian contribution centred at its approximate photopic peak wavelength:
        Blue  → 460 nm  (σ = 30 nm)
        Green → 540 nm  (σ = 35 nm)
        Red   → 620 nm  (σ = 40 nm)
    The three Gaussians are summed and normalised to give a qualitative
    reflectance curve over the visible range.

    NOTE: This is an *educational approximation*, not a true spectrometer
    reading. A real plant spectrum requires a spectrometer.
    """
    all_paths = [("Mystery Plant", unknown_path)] + \
                [(p["name"], _path(p)) for p in known_plants]
    n   = len(all_paths)
    wl  = np.linspace(400, 780, 800)

    # Channel definitions: (name, peak nm, sigma nm, channel index in RGB)
    CH = [("Blue",  460, 30, 2),
          ("Green", 540, 35, 1),
          ("Red",   620, 40, 0)]
    ch_colors = {"Blue": "#4472C4", "Green": "#2E8B57", "Red": "#C0392B"}

    # Build rainbow background as an RGBA image (1 × N pixels)
    rainbow = np.array([[_wavelength_to_rgb(w) for w in wl]])  # shape (1, 800, 3)

    fig, axes = plt.subplots(n, 1, figsize=(11, 2.8 * n), sharex=True)
    if n == 1:
        axes = [axes]

    for ax, (name, path) in zip(axes, all_paths):
        # Draw rainbow strip at the bottom quarter of each subplot
        ax.imshow(rainbow, extent=[400, 780, 0, 0.28],
                  aspect="auto", origin="lower", alpha=0.75, zorder=0)

        try:
            img   = np.array(Image.open(path).convert("RGB"))
            means = img.mean(axis=(0, 1)) / 255.0   # (R_mean, G_mean, B_mean)
        except Exception:
            ax.text(0.5, 0.5, f"Cannot open {name}", ha="center",
                    va="center", transform=ax.transAxes, color="#cc3333")
            continue

        # Build composite pseudo-spectrum
        composite = np.zeros_like(wl)
        for ch_name, centre, sigma, idx in CH:
            weight   = float(means[idx])
            gauss    = weight * np.exp(-0.5 * ((wl - centre) / sigma) ** 2)
            ax.plot(wl, gauss, color=ch_colors[ch_name],
                    lw=1.2, alpha=0.6, linestyle="--",
                    label=f"{ch_name} channel (peak {centre} nm)")
            composite += gauss

        # Normalise composite
        if composite.max() > 0:
            composite /= composite.max()

        ax.fill_between(wl, composite, alpha=0.25, color="#888888", zorder=1)
        ax.plot(wl, composite, color="#111111", lw=2.0, zorder=2,
                label="Combined spectrum")

        # Mark the three channel peaks
        for ch_name, centre, sigma, idx in CH:
            ax.axvline(centre, color=ch_colors[ch_name],
                       lw=0.8, linestyle=":", alpha=0.8)
            ax.text(centre, 1.05, f"{centre} nm",
                    ha="center", fontsize=7, color=ch_colors[ch_name])

        is_mystery = (name == "Mystery Plant")
        ax.set_title(
            f"[?] {name}  (B={means[2]:.2f}  G={means[1]:.2f}  R={means[0]:.2f})"
            if is_mystery else
            f"[K] {name}  (B={means[2]:.2f}  G={means[1]:.2f}  R={means[0]:.2f})",
            fontsize=11, fontweight="bold",
            color="#333333" if is_mystery else "#2d6a2d")
        ax.set_ylim(0, 1.18)
        ax.set_ylabel("Relative\nreflectance", fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].legend(loc="upper right", fontsize=8, framealpha=0.8)

    # Wavelength labels for common colours
    ax_bot = axes[-1]
    ax_bot.set_xlabel("Wavelength  (nm)", fontsize=11)
    for wl_label, txt in [(420,"Violet"),(470,"Blue"),(520,"Cyan"),
                           (560,"Green"),(600,"Yellow"),(650,"Orange"),(700,"Red")]:
        ax_bot.text(wl_label, -0.18, txt, ha="center", fontsize=7,
                    color=ch_colors.get(txt, "#555"), transform=ax_bot.get_xaxis_transform())

    fig.suptitle(
        "Approximate visible-light reflectance spectra  (400–780 nm)\n"
        "Dashed lines = individual R / G / B channel contributions",
        fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.show()

    print("Note: These are educational pseudo-spectra based on camera RGB values,")
    print("not true spectrometer measurements. Peak wavelengths are approximate.")

# ── Color spectrum plot ────────────────────────────────────────────────────────

def plot_color_spectra(unknown_path, known_plants, bins=64):
    """
    Plot RGB intensity spectra for the mystery plant and each known plant
    side by side, like emission spectra.
    """
    all_paths = [("Mystery Plant", unknown_path)] + \
                [(p["name"], _path(p)) for p in known_plants]
    n = len(all_paths)
    ch_colors = {"Red": "#e05050", "Green": "#3a9e3a", "Blue": "#4070d0"}

    fig, axes = plt.subplots(n, 1, figsize=(10, 2.8 * n), sharex=True)
    if n == 1:
        axes = [axes]

    edges = np.linspace(0, 255, bins + 1)
    centres = 0.5 * (edges[:-1] + edges[1:])

    for ax, (name, path) in zip(axes, all_paths):
        try:
            hists = color_histogram(path, bins=bins)
        except Exception:
            ax.text(0.5, 0.5, f"Cannot open {name}", ha="center",
                    va="center", transform=ax.transAxes, color="#cc3333")
            continue
        for ch, color in ch_colors.items():
            ax.fill_between(centres, hists[ch], alpha=0.35, color=color)
            ax.plot(centres, hists[ch], color=color, lw=1.2, label=ch)
        ax.set_ylabel("Fraction\nof pixels", fontsize=9)
        ax.set_title(f"{'[?]' if name == 'Mystery Plant' else '[K]'} {name}",
                     fontsize=11, fontweight="bold",
                     color="#333333" if name == "Mystery Plant" else "#2d6a2d")
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylim(bottom=0)

    axes[0].legend(loc="upper right", fontsize=9, framealpha=0.7)
    axes[-1].set_xlabel("Pixel intensity  (0 = dark,  255 = bright)", fontsize=10)
    fig.suptitle("RGB colour intensity spectra", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.show()


def plot_hue_spectra(unknown_path, known_plants, bins=36):
    """
    Plot hue angle distributions (0°–360°) for all plants.
    Each bar is coloured with its actual hue so the chart is self-explanatory.
    """
    all_paths = [("Mystery Plant", unknown_path)] + \
                [(p["name"], _path(p)) for p in known_plants]
    n = len(all_paths)

    fig, axes = plt.subplots(1, n, figsize=(4 * n, 3.5))
    if n == 1:
        axes = [axes]

    import colorsys
    for ax, (name, path) in zip(axes, all_paths):
        try:
            centres, counts = hue_histogram(path, bins=bins)
        except Exception:
            continue
        bar_colors = [colorsys.hsv_to_rgb(h / 360, 0.85, 0.85)
                      for h in centres]
        ax.bar(centres, counts, width=360 / bins,
               color=bar_colors, edgecolor="none")
        ax.set_xlim(0, 360)
        ax.set_xlabel("Hue angle (°)", fontsize=9)
        ax.set_ylabel("Fraction of coloured pixels", fontsize=9)
        ax.set_title(f"{'[?]' if name == 'Mystery Plant' else '[K]'} {name}",
                     fontsize=11, fontweight="bold",
                     color="#333333" if name == "Mystery Plant" else "#2d6a2d")
        ax.set_xticks([0, 60, 120, 180, 240, 300, 360])
        ax.set_xticklabels(["0°\nRed", "60°\nYellow", "120°\nGreen",
                             "180°\nCyan", "240°\nBlue", "300°\nMagenta", "360°"])
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Hue angle spectra  (coloured pixels only)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_dominant_colors(unknown_path, known_plants, n_colors=6):
    """
    Show dominant colour swatches for every plant as stacked bars.
    """
    all_paths = [("Mystery Plant", unknown_path)] + \
                [(p["name"], _path(p)) for p in known_plants]
    n = len(all_paths)

    fig, axes = plt.subplots(n, 1, figsize=(9, 1.6 * n))
    if n == 1:
        axes = [axes]

    for ax, (name, path) in zip(axes, all_paths):
        try:
            palette = dominant_colors(path, n_colors=n_colors)
        except Exception:
            continue
        left = 0
        for prop, rgb in palette:
            hex_col = "#{:02x}{:02x}{:02x}".format(*rgb)
            fc = [c / 255 for c in rgb]
            ax.barh(0, prop, left=left, color=fc, height=0.6)
            if prop > 0.06:
                lum = 0.299 * fc[0] + 0.587 * fc[1] + 0.114 * fc[2]
                tx_col = "white" if lum < 0.5 else "#333"
                ax.text(left + prop / 2, 0, f"{hex_col}\n{prop*100:.0f}%",
                        ha="center", va="center", fontsize=8,
                        color=tx_col, fontweight="bold")
            left += prop
        ax.set_xlim(0, 1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_ylabel(f"{'[?]' if name == 'Mystery Plant' else '[K]'} {name}",
                      fontsize=10, fontweight="bold", rotation=0,
                      labelpad=4, ha="right", va="center",
                      color="#333333" if name == "Mystery Plant" else "#2d6a2d")
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.suptitle("Dominant colour composition", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


def compare_plants_full(unknown_path, known_plants, clip_weight=0.6):
    """
    Compare plants using both CLIP embeddings AND colour similarity,
    then combine into a single ranked score.

    Parameters
    ----------
    clip_weight : float
        Weight for CLIP score (0–1). Colour gets 1 - clip_weight.

    Returns
    -------
    dict with 'clip', 'color', 'combined' similarity tables
    """
    print("Computing CLIP embeddings…")
    unknown_emb = get_embedding(unknown_path)

    rows = []
    for plant in known_plants:
        p = _path(plant)
        name = plant["name"]

        # CLIP similarity
        known_emb  = get_embedding(p)
        raw_cosine = (unknown_emb @ known_emb.T).item()
        clip_score = _rescale(raw_cosine)

        # Colour similarity
        col_score = color_similarity(unknown_path, p)

        # Combined
        combined = clip_weight * clip_score + (1 - clip_weight) * col_score

        rows.append({
            "name":     name,
            "clip":     round(clip_score,  3),
            "color":    round(col_score,   3),
            "combined": round(combined,    3),
        })
        print(f"  {name:20s}  CLIP {clip_score*100:.0f}%  "
              f"Colour {col_score*100:.0f}%  Combined {combined*100:.0f}%")

    rows.sort(key=lambda x: x["combined"], reverse=True)
    return {"similarities": rows, "best_match": rows[0]["name"],
            "clip_weight": clip_weight, "color_weight": 1 - clip_weight}


def plot_combined_results(result):
    """
    Grouped bar chart showing CLIP, colour, and combined scores side by side.
    """
    sims  = result["similarities"]
    names = [s["name"] for s in sims]
    clips = [s["clip"]     for s in sims]
    cols  = [s["color"]    for s in sims]
    comb  = [s["combined"] for s in sims]

    x    = np.arange(len(names))
    w    = 0.25
    fig, ax = plt.subplots(figsize=(9, max(3.5, len(names) * 1.1)))

    ax.barh(x + w,   clips, w, color="#4a90d9", label=f"CLIP visual  "
            f"(×{result['clip_weight']:.0%})",  edgecolor="white")
    ax.barh(x,       cols,  w, color="#3aaa3a", label=f"Colour match "
            f"(×{result['color_weight']:.0%})", edgecolor="white")
    ax.barh(x - w,   comb,  w, color="#7b4ea0", label="Combined score",
            edgecolor="white")

    for i, (c, co, cb) in enumerate(zip(clips, cols, comb)):
        ax.text(min(c  + 0.02, 1.07), i + w,   f"{c*100:.0f}%",  va="center", fontsize=9)
        ax.text(min(co + 0.02, 1.07), i,        f"{co*100:.0f}%", va="center", fontsize=9)
        ax.text(min(cb + 0.02, 1.07), i - w,    f"{cb*100:.0f}%", va="center", fontsize=9,
                fontweight="bold", color="#7b4ea0")

    ax.set_yticks(x)
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Similarity score", fontsize=11)
    ax.set_title(f"Multi-metric plant similarity\nBest match: {result['best_match']}",
                 fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()
