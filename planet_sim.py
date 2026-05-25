"""
planet_sim.py
=============
Backend module for the Planet Builder simulation activity.
Designed for 7th/8th grade science — import this file and call build_ui().

Usage in notebook:
    from planet_sim import build_ui
    build_ui()
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')   # set before pyplot import to avoid backend warnings in JupyterHub
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import time

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
DARK_BG    = '#0f0f23'
PANEL_BG   = '#1a1a2e'
GRID_COLOR = '#2a2a4e'

WATER_LABELS = {0: 'Frozen Ice',   1: 'Liquid Ocean',  2: 'Boiling Vapor'}
WATER_EMOJI  = {0: '❄️',           1: '🌊',             2: '♨️'}
WATER_COLORS = {0: '#74b9ff',      1: '#00cec9',        2: '#fd79a8'}
PLANET_FACE  = {0: '#4a90d9',      1: '#00897b',        2: '#c0392b'}

# Messages shown while simulation runs — deliberately paced for drama
SIM_MESSAGES = [
    ("🪐", "Assembling planet from dust and gas"),
    ("☀️", "Calculating stellar energy input"),
    ("🌋", "Starting volcanic outgassing"),
    ("🌡️", "Running energy balance equations"),
    ("💧", "Simulating the water cycle"),
    ("🌫️", "Modelling greenhouse gas layers"),
    ("🧊", "Checking ice–albedo feedback"),
    ("⏳", "Fast-forwarding 600 million years"),
    ("🧬", "Scanning for signs of life"),
    ("📊", "Preparing your results"),
]

# Planet presets  (distance_au, luminosity, co2_pct, h2o_pct, mass_earth)
PRESETS = {
    "🌍 Earth-like"        : (1.00, 1.00,  5.0, 1.0, 1.00),
    "🔴 Mars-like"         : (1.52, 1.00,  0.1, 0.0, 0.11),
    "🌋 Early Venus"       : (0.72, 1.00, 10.0, 2.0, 0.82),
    "🧊 Snowball Earth"    : (1.00, 0.94,  2.0, 3.0, 1.00),
    "⭐ Close to a Dim Star": (0.35, 0.25,  8.0, 1.5, 0.90),
    "🌙 Tiny Cold World"   : (1.30, 0.80,  1.0, 0.5, 0.20),
}

# ─────────────────────────────────────────────────────────────
# PHYSICS ENGINE
# ─────────────────────────────────────────────────────────────

def _equilibrium_temp(distance_au, luminosity_solar, albedo):
    """
    Stefan-Boltzmann energy balance temperature (Kelvin).
    No atmosphere — just the raw balance between absorbed and emitted radiation.
    """
    return 278.5 * (luminosity_solar ** 0.25) / np.sqrt(distance_au) * ((1.0 - albedo) ** 0.25)


def simulate_planet(distance_au, luminosity, initial_co2_pct,
                    initial_h2o_pct, mass_earth,
                    n_steps=300, total_Myr=600):
    """
    Simulate atmospheric and temperature evolution over time.

    Parameters
    ----------
    distance_au      : float  — distance from host star in AU
    luminosity       : float  — stellar brightness (1.0 = Sun)
    initial_co2_pct  : float  — starting CO₂ as % of atmosphere
    initial_h2o_pct  : float  — starting water vapour as % of atmosphere
    mass_earth       : float  — planet mass in Earth masses
    n_steps          : int    — number of simulation time steps
    total_Myr        : float  — total time span in millions of years

    Returns
    -------
    dict with keys:
        times, T_celsius, co2_pct, water_state, habitability
    """
    dt    = total_Myr / n_steps
    times = np.linspace(0, total_Myr, n_steps)

    co2    = initial_co2_pct  / 100.0
    h2o    = initial_h2o_pct  / 100.0
    albedo = 0.30

    T_arr   = np.zeros(n_steps)
    co2_arr = np.zeros(n_steps)
    ws_arr  = np.zeros(n_steps, dtype=int)
    hab_arr = np.zeros(n_steps)

    # Hysteresis: start in whichever phase the initial conditions imply
    T_eq_init   = _equilibrium_temp(distance_au, luminosity, albedo)
    T_init      = T_eq_init + 80.0 * co2 + 25.0 * min(h2o, 0.05) / 0.05
    water_state = 1 if 273 < T_init < 373 else (2 if T_init >= 373 else 0)

    # Deterministic seed varies per planet for unique early volcanic history
    _seed = int(abs(distance_au * 137 + luminosity * 97 + mass_earth * 53)) % 1000

    for i in range(n_steps):
        frac_age = i / n_steps

        # Energy balance + greenhouse
        T_eq        = _equilibrium_temp(distance_au, luminosity, albedo)
        co2_warming = 80.0 * co2
        h2o_warming = 25.0 * min(h2o, 0.05) / 0.05
        T           = T_eq + co2_warming + h2o_warming   # Kelvin

        # Early-planet variability: episodic volcanic pulses (first 35%)
        # Mimics large igneous province events / heavy bombardment era.
        if frac_age < 0.35:
            pulse = np.sin((_seed + i) * 0.43) * np.sin((_seed + i) * 1.17)
            if pulse > 0.82:
                co2 = min(co2 + 0.012 * mass_earth * (1 - frac_age / 0.35), 0.98)

        # Water phase with HYSTERESIS -- requires crossing a margin to switch,
        # so the planet cannot oscillate every step at phase boundaries.
        if water_state == 0:          # ICE: needs +5 K margin to melt
            if T >= 278.15:
                water_state = 1
        elif water_state == 1:        # LIQUID: margins on both sides
            if T < 268.15:
                water_state = 0       # needs -5 K to freeze
            elif T >= 383.15:
                water_state = 2       # needs +10 K to boil
        else:                         # VAPOUR: needs -10 K margin to condense
            if T < 363.15:
                water_state = 1

        # Phase-specific feedbacks
        if water_state == 0:
            target_albedo = 0.30 + 0.50 * min(h2o, 0.5)
            co2 = min(co2 + 0.0008 * mass_earth * (1 - 0.6*frac_age) * dt, 0.98)
            h2o = max(h2o - 0.00005 * dt, 0.0)

        elif water_state == 1:
            target_albedo = 0.28
            ocean_eff = max(0.0, 1.0 - (T - 273) / 150)
            co2 = max(co2 - 0.003 * ocean_eff * dt, 0.0001)
            h2o = min(h2o + 0.0002 * (T - 273) / 100 * dt, 0.10)

        else:
            target_albedo = 0.42
            h2o = min(h2o + 0.001 * dt, 0.60)
            co2 = min(co2 + 0.0005 * mass_earth * dt, 0.98)

        # Volcanic outgassing (slows as planet ages)
        co2 = min(co2 + 0.0006 * mass_earth * (1 - 0.75*frac_age) * dt, 0.98)

        # Atmospheric escape (small planets lose their air)
        if mass_earth < 0.5:
            loss = 0.0015 * (0.5 - mass_earth) * dt
            co2  = max(co2 - loss,       0.0)
            h2o  = max(h2o - loss * 0.6, 0.0)

        # Smooth albedo transition
        albedo = 0.85 * albedo + 0.15 * target_albedo

        # Raw habitability score
        if water_state == 1 and co2 < 0.90:
            hab = max(0.0, 1.0 - abs((T - 288) / 45))
        else:
            hab = 0.0

        T_arr[i]   = T - 273.15
        co2_arr[i] = co2 * 100.0
        ws_arr[i]  = water_state
        hab_arr[i] = hab

    # Rolling-window smooth removes flicker near phase boundaries
    win     = max(1, n_steps // 25)
    hab_arr = np.convolve(hab_arr, np.ones(win) / win, mode='same')

    return dict(times=times, T_celsius=T_arr, co2_pct=co2_arr,
                water_state=ws_arr, habitability=hab_arr)


# ─────────────────────────────────────────────────────────────
# PROGRESS DISPLAY
# ─────────────────────────────────────────────────────────────

def _show_progress(out, step, total, emoji, message):
    """Render a styled progress card inside an Output widget."""
    pct   = int((step / total) * 100)
    dots  = "█" * (pct // 5) + "░" * (20 - pct // 5)
    html  = f"""
    <div style="
        background: {PANEL_BG};
        border: 1px solid #444466;
        border-radius: 12px;
        padding: 24px 28px;
        font-family: 'Courier New', monospace;
        max-width: 520px;
    ">
      <div style="font-size: 48px; margin-bottom: 12px; text-align:center">{emoji}</div>
      <div style="color: #7eb8f7; font-size: 18px; margin-bottom: 6px;
                  text-align:center; font-weight:bold">PLANET BUILDER</div>
      <div style="color: #aaaacc; font-size: 13px; margin-bottom: 16px;
                  text-align:center">{message}…</div>
      <div style="background: #0f0f23; border-radius: 6px; padding: 4px 8px;
                  font-size: 12px; color: #55efc4; letter-spacing: 2px;
                  font-family: monospace">
        [{dots}] {pct}%
      </div>
      <div style="color:#444466; font-size:11px; margin-top:8px; text-align:right">
        Step {step} / {total}
      </div>
    </div>
    """
    with out:
        clear_output(wait=True)
        display(HTML(html))


def _run_with_drama(out, fn, delay=0.28):
    """
    Show SIM_MESSAGES one by one (with delays for drama),
    then call fn() and display results.
    """
    total = len(SIM_MESSAGES)
    for i, (emoji, msg) in enumerate(SIM_MESSAGES, start=1):
        _show_progress(out, i, total, emoji, msg)
        time.sleep(delay)
    return fn()


# ─────────────────────────────────────────────────────────────
# PLOTTING  — simplified for middle school
# ─────────────────────────────────────────────────────────────

def _draw_planet_portrait(ax, ws_final, T_final, hab_max):
    """
    Draw a stylised planet circle with stars, coloured by water phase,
    plus a large habitability score.
    """
    ax.set_facecolor('#000011')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Starfield
    rng = np.random.default_rng(42)
    sx  = rng.uniform(0, 10, 80)
    sy  = rng.uniform(0, 10, 80)
    ss  = rng.uniform(1, 6,  80)
    ax.scatter(sx, sy, s=ss, c='white', alpha=0.55, zorder=1)

    # Atmosphere glow
    glow_color = PLANET_FACE[ws_final]
    glow = patches.Circle((5, 5.8), radius=2.7,
                           color=glow_color, alpha=0.18, zorder=2)
    ax.add_patch(glow)

    # Planet body
    planet = patches.Circle((5, 5.8), radius=2.2,
                             color=PLANET_FACE[ws_final], zorder=3)
    ax.add_patch(planet)

    # Surface detail
    if ws_final == 1:          # liquid — draw ocean shine patches
        for cx, cy, r in [(4.2, 6.4, 0.55), (5.8, 5.2, 0.40), (4.8, 4.8, 0.30)]:
            ocean = patches.Ellipse((cx, cy), r * 1.6, r,
                                    color='#81ecec', alpha=0.35, zorder=4)
            ax.add_patch(ocean)
    elif ws_final == 0:        # ice — polar cap
        cap = patches.Ellipse((5, 7.6), 1.8, 0.6,
                              color='white', alpha=0.55, zorder=4)
        ax.add_patch(cap)
    else:                      # vapor — cloud wisps
        for cx, cy in [(4.0, 6.2), (5.5, 5.0), (5.2, 7.0)]:
            cloud = patches.Ellipse((cx, cy), 1.4, 0.45,
                                    color='#fab1a0', alpha=0.40, zorder=4)
            ax.add_patch(cloud)

    # Water-state label (no emoji — matplotlib font lacks emoji glyphs)
    label = WATER_LABELS[ws_final]
    ax.text(5, 2.8, label, ha='center', va='center',
            color=WATER_COLORS[ws_final], fontsize=12, fontweight='bold', zorder=6)

    # Temperature
    ax.text(5, 2.15, f"Surface: {T_final:+.0f} °C", ha='center', va='center',
            color='#dfe6e9', fontsize=10, zorder=6)

    # Habitability gauge bar
    hab_pct = int(hab_max * 100)
    bar_color = '#55efc4' if hab_pct >= 40 else '#fdcb6e' if hab_pct >= 10 else '#e17055'
    ax.text(5, 1.35, f"Life Score: {hab_pct}%", ha='center', va='center',
            color=bar_color, fontsize=13, fontweight='bold', zorder=6)

    # Gauge track
    track = patches.FancyBboxPatch((1.5, 0.65), 7, 0.5,
                                   boxstyle='round,pad=0.05',
                                   color='#2d3436', zorder=5)
    ax.add_patch(track)
    fill_w = 7 * hab_max
    if fill_w > 0:
        fill = patches.FancyBboxPatch((1.5, 0.65), fill_w, 0.5,
                                      boxstyle='round,pad=0.05',
                                      color=bar_color, zorder=6)
        ax.add_patch(fill)

    ax.set_title('Your Planet', color='white', fontsize=11,
                 fontweight='bold', pad=4)


def plot_results(results, dist, lum, co2_0, h2o_0, mass):
    """
    Three-panel results figure designed for 7th/8th graders:
      Left  — temperature timeline with labelled zones
      Middle — water phase colour strip
      Right  — planet portrait + life score
    """
    times   = results['times']
    T       = results['T_celsius']
    co2     = results['co2_pct']
    ws      = results['water_state']
    hab     = results['habitability']

    ws_final  = int(ws[-1])
    T_final   = T[-1]
    hab_max   = hab.max()
    hab_Myr   = int((hab > 0.3).sum() * (times[1] - times[0]))

    fig = plt.figure(figsize=(14, 4.6), facecolor=DARK_BG)
    gs  = gridspec.GridSpec(1, 3, figure=fig,
                            wspace=0.40, left=0.07, right=0.97,
                            top=0.82, bottom=0.16)

    # ── Panel 1: Temperature Timeline ────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(PANEL_BG)

    # Coloured zone bands
    ax1.axhspan(-273, -20,  alpha=0.18, color='#74b9ff', label='Too Cold')
    ax1.axhspan(-20,   60,  alpha=0.18, color='#55efc4', label='Habitable Zone')
    ax1.axhspan(60,   600,  alpha=0.18, color='#fd79a8', label='Too Hot')

    ax1.plot(times, T, color='white', linewidth=2.5, zorder=4)
    ax1.axhline(0,   color='#74b9ff', lw=1, ls='--', alpha=0.7)
    ax1.axhline(100, color='#fd79a8', lw=1, ls='--', alpha=0.7)

    ax1.set_xlim(0, times[-1])
    ylo_v = max(T.min() - 30, -250)
    yhi_v = min(T.max() + 30, 550)
    ax1.set_ylim(ylo_v, yhi_v)

    # Zone labels — placed in axes-fraction space so they always stay inside the panel
    def _band_frac(y_data):
        """Convert a data-coordinate y to an axes fraction, clamped to [0.05, 0.95]."""
        return float(np.clip((y_data - ylo_v) / (yhi_v - ylo_v), 0.05, 0.95))

    ax1.text(0.97, _band_frac(-120), 'Too Cold', ha='right', va='center',
             transform=ax1.transAxes,
             color='#74b9ff', fontsize=8.5, style='italic')
    ax1.text(0.97, _band_frac(20),   'Life Zone', ha='right', va='center',
             transform=ax1.transAxes,
             color='#55efc4', fontsize=8.5, style='italic')
    ax1.text(0.97, _band_frac(300),  'Too Hot', ha='right', va='center',
             transform=ax1.transAxes,
             color='#fd79a8', fontsize=8.5, style='italic')
    ax1.set_xlabel('Time (millions of years)', color='white', fontsize=10)
    ax1.set_ylabel('Surface Temperature (°C)', color='white', fontsize=10)
    ax1.set_title('Temperature Over Time', color='white',
                  fontsize=11, fontweight='bold', pad=5)
    ax1.tick_params(colors='white')
    ax1.grid(True, color=GRID_COLOR, linewidth=0.6)
    for sp in ax1.spines.values():
        sp.set_edgecolor('#444466')

    # ── Panel 2: Water Phase Strip + CO₂ ─────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(PANEL_BG)

    # Stacked area: colour-code each time step by water phase
    for i in range(len(times) - 1):
        ax2.axvspan(times[i], times[i+1],
                    ymin=0.55, ymax=1.0,
                    color=WATER_COLORS[ws[i]], alpha=0.85)

    # CO₂ curve in lower half
    # Normalise CO₂ to 0–0.5 range for the lower panel portion
    co2_norm = np.clip(co2 / 100.0, 0, 1) * 0.50
    ax2.fill_between(times, 0, co2_norm,
                     color='#fdcb6e', alpha=0.75, label='CO₂ level')
    ax2.plot(times, co2_norm, color='#fdcb6e', linewidth=1.5)

    # Divider line
    ax2.axhline(0.53, color='#444466', linewidth=1)

    # Phase legend patches
    import matplotlib.patches as mpatches
    phase_patches = [mpatches.Patch(color=WATER_COLORS[s],
                                    label=WATER_LABELS[s]) for s in [0, 1, 2]]
    phase_patches.append(mpatches.Patch(color='#fdcb6e', alpha=0.8, label='CO₂ level'))
    ax2.legend(handles=phase_patches, loc='lower left',
               fontsize=7.5, facecolor=PANEL_BG, labelcolor='white',
               edgecolor='#444466', framealpha=0.9)

    # Labels
    ax2.text(times[-1] * 0.02, 0.77,  'WATER PHASE', color='white',
             fontsize=8, fontweight='bold', va='center')
    ax2.text(times[-1] * 0.02, 0.25, 'CO₂ IN\nATMOSPHERE', color='#fdcb6e',
             fontsize=7.5, va='center')

    ax2.set_yticks([])
    ax2.set_xlabel('Time (millions of years)', color='white', fontsize=10)
    ax2.set_title('Water Phase & CO2', color='white',
                  fontsize=11, fontweight='bold', pad=5)
    ax2.set_xlim(0, times[-1])
    ax2.set_ylim(0, 1)
    ax2.tick_params(colors='white')
    for sp in ax2.spines.values():
        sp.set_edgecolor('#444466')

    # ── Panel 3: Planet Portrait ──────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    _draw_planet_portrait(ax3, ws_final, T_final, hab_max)

    # ── Overall title ─────────────────────────────────────────
    if hab_max > 0.5:
        verdict = ">> Life seems possible on this world!"
        vcolor  = '#55efc4'
    elif hab_max > 0.1:
        verdict = f"~ Briefly habitable -- {hab_Myr} million years"
        vcolor  = '#fdcb6e'
    else:
        verdict = "X Too harsh -- no life could survive here"
        vcolor  = '#e17055'

    fig.suptitle(verdict, y=0.99, ha='center', va='top',
                 color=vcolor, fontsize=12, fontweight='bold')

    plt.savefig('/tmp/planet_result.png', dpi=120, facecolor=DARK_BG,
                bbox_inches='tight')
    plt.show()
    plt.close(fig)

    # Text summary
    print("\n" + "═" * 52)
    print("  MISSION REPORT")
    print("═" * 52)
    print(f"  Final temperature : {T_final:+.1f} °C")
    print(f"  Final water phase : {WATER_LABELS[ws_final]}")
    print(f"  Final CO₂         : {co2[-1]:.2f} %")
    print(f"  Peak life score   : {int(hab_max*100)} / 100")
    if hab_Myr > 0:
        print(f"  Habitable window  : {hab_Myr} million years")
    print("═" * 52)


# ─────────────────────────────────────────────────────────────
# WIDGET UI  — everything the notebook student sees
# ─────────────────────────────────────────────────────────────

def build_ui():
    """
    Build and display the complete Planet Builder interface.
    Call this from a notebook cell: from planet_sim import build_ui; build_ui()
    """
    SL   = {'description_width': '160px'}
    LAY  = widgets.Layout(width='440px')
    BLAY = widgets.Layout(width='200px', height='42px')

    # ── Sliders ───────────────────────────────────────────────
    w_dist = widgets.FloatSlider(
        value=1.0, min=0.3, max=3.5, step=0.05,
        description='🌟 Distance (AU)', style=SL, layout=LAY,
        readout_format='.2f',
        tooltip='1 AU = Earth–Sun distance')

    w_lum = widgets.FloatSlider(
        value=1.0, min=0.1, max=2.5, step=0.05,
        description='☀️  Star Brightness', style=SL, layout=LAY,
        readout_format='.2f',
        tooltip='1.0 = same as our Sun')

    w_co2 = widgets.FloatSlider(
        value=5.0, min=0.01, max=96.0, step=0.5,
        description='🌫️  Starting CO₂ (%)', style=SL, layout=LAY,
        readout_format='.1f',
        tooltip="Earth today: 0.04%  |  Venus: 96%  |  Mars: 95%")

    w_h2o = widgets.FloatSlider(
        value=1.0, min=0.0, max=10.0, step=0.1,
        description='💧 Starting Water (%)', style=SL, layout=LAY,
        readout_format='.1f',
        tooltip='Water vapour in the starting atmosphere')

    w_mass = widgets.FloatSlider(
        value=1.0, min=0.1, max=5.0, step=0.05,
        description='🪨 Planet Mass (Earths)', style=SL, layout=LAY,
        readout_format='.2f',
        tooltip='Small planets lose their atmosphere faster')

    # ── Preset dropdown ───────────────────────────────────────
    preset_keys = ['— choose a preset —'] + list(PRESETS.keys())
    w_preset = widgets.Dropdown(
        options=preset_keys,
        value='— choose a preset —',
        description='🔧 Quick Preset:',
        style=SL, layout=LAY)

    def apply_preset(change):
        key = w_preset.value
        if key in PRESETS:
            d, l, c, h, m = PRESETS[key]
            w_dist.value  = d
            w_lum.value   = l
            w_co2.value   = c
            w_h2o.value   = h
            w_mass.value  = m

    w_preset.observe(apply_preset, names='value')

    # ── Buttons ───────────────────────────────────────────────
    btn_run   = widgets.Button(description='▶  RUN SIMULATION',
                               button_style='success', layout=BLAY)
    btn_reset = widgets.Button(description='↩  Reset to Earth',
                               button_style='info',
                               layout=widgets.Layout(width='160px', height='42px'))

    def reset_earth(_):
        w_preset.value = '— choose a preset —'
        w_dist.value   = 1.0
        w_lum.value    = 1.0
        w_co2.value    = 5.0
        w_h2o.value    = 1.0
        w_mass.value   = 1.0

    btn_reset.on_click(reset_earth)

    # ── Output widget ─────────────────────────────────────────
    out = widgets.Output()

    def on_run(_):
        dist = w_dist.value
        lum  = w_lum.value
        co2  = w_co2.value
        h2o  = w_h2o.value
        mass = w_mass.value

        def _do_sim():
            results = simulate_planet(dist, lum, co2, h2o, mass)
            with out:
                clear_output(wait=True)
                plot_results(results, dist, lum, co2, h2o, mass)

        _run_with_drama(out, _do_sim)

    btn_run.on_click(on_run)

    # ── Layout assembly ───────────────────────────────────────
    header = widgets.HTML("""
    <div style="
        background: #1a1a2e;
        border: 1px solid #444466;
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 6px;
        font-family: sans-serif;
    ">
      <span style="font-size:22px">🪐</span>
      <span style="color:#7eb8f7; font-size:18px; font-weight:bold;
                   margin-left:8px">Planet Builder</span>
      <div style="color:#aaaacc; font-size:12px; margin-top:4px">
        Set your planet's starting conditions below, then click
        <b style="color:#55efc4">▶ RUN SIMULATION</b>.
      </div>
    </div>
    """)

    tip = widgets.HTML("""
    <div style="color:#aaaacc; font-size:11px; font-style:italic;
                margin: 4px 0 0 4px">
      💡 Tip: Try a preset first, then tweak the sliders to see what changes!
    </div>""")

    ui = widgets.VBox([
        header,
        w_preset,
        widgets.HTML("<div style='height:6px'></div>"),
        w_dist, w_lum, w_co2, w_h2o, w_mass,
        widgets.HTML("<div style='height:8px'></div>"),
        widgets.HBox([btn_run, widgets.HTML("&nbsp;&nbsp;"), btn_reset]),
        tip,
        widgets.HTML("<div style='height:10px'></div>"),
        out,
    ], layout=widgets.Layout(padding='10px'))

    display(ui)
