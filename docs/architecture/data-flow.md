---
title: Data Flow
date: 2025-11-05
status: Active
---

# Data Flow Through the Pipeline

This document details how data moves through the Klutz Workbook generation pipeline, with examples at each stage.

## Complete Pipeline Flow

```
YAML Layout → Prompt Gen → Gemini → nano-banana → Validation → Compositor → Post-Process → QA → PDF
```

---

## Stage 1: Layout Definition

### Input: Designer Intent

**Human-readable specifications:**
- "Page 4-5 should introduce pixel art"
- "Left page has headline and photo of mouse"
- "Right page has example pixel art in a yellow box"

### Output: Layout YAML

**File:** `config/layouts/spread_04_05.yaml`

```yaml
spread_info:
  number: "04-05"
  title: "Pixel Perfect! Making Your First Sprite"
  template: "workshop_layout"

left_page:
  elements:
    - id: "L_headline_pixelart_01"
      type: "text_headline"
      content: "PIXEL PERFECT!"
      position: [200, 180]
      # ... more properties ...
```

**Data Format:** YAML (human-editable text)
**Size:** ~2-5 KB per spread

---

## Stage 2: Prompt Generation

### Input: Layout YAML + Master Config

**Read Files:**
- `config/layouts/spread_04_05.yaml`
- `config/master_config.yaml`

**Processing:**
```python
for element in layout['left_page']['elements']:
    if element['type'] == 'graphic_photo_instructional':
        prompt = generator.generate_photo_prompt(element)
```

### Output: XML Prompt Files

**File:** `prompts/spread_04_05/L_photo_mouse_01.xml`

```xml
<prompt>
  <subject>
    A photograph of a beige one-button Apple Macintosh M0100 mouse
    in the hands of a person using it on a wooden desk surface
  </subject>
  <perspective>
    Photographed from above at a 45-degree angle, showing both the
    mouse and the hand clearly
  </perspective>
  <lighting>
    Natural indoor lighting from a window, soft shadows to the right,
    no artificial studio lighting
  </lighting>
  <technical>
    Photographed with a consumer-grade film camera, slight grain,
    colors typical of 1990s Kodak film processing
  </technical>
  <constraints>
    - No modern technology visible
    - No gradients or soft focus
    - Hard-edged shadows only
    - Beige/cream color palette
  </constraints>
</prompt>
```

**Data Format:** XML (structured text)
**Size:** ~1-2 KB per prompt
**Count:** ~5-15 prompts per spread

---

## Stage 3: Prompt Refinement

### Input: Base XML Prompt

**Processing:**
```python
refined = gemini.refine_prompt(base_prompt)
```

**Gemini API Request:**
```json
{
  "model": "gemini-pro",
  "prompt": "Refine this image generation prompt...",
  "temperature": 0.3
}
```

### Output: Refined Prompt

**Enhanced specificity:**
- Added contextual details
- Clarified ambiguous terms
- Reinforced period constraints
- Improved structural clarity

**Data Format:** Enhanced XML
**Size:** ~2-3 KB per prompt
**Processing Time:** ~2-5 seconds

---

## Stage 4: Image Generation

### Input: Refined XML Prompt + Dimensions

**nano-banana Request:**
```python
image = nano_banana.generate_image(
    prompt=refined_prompt,
    dimensions=(800, 600),
    style="photographic",
    quality="high"
)
```

### Output: Generated PNG Asset

**File:** `assets/generated/photo_mouse_01.png`

**Properties:**
- Dimensions: 800x600 pixels
- Format: PNG with alpha channel
- Color depth: 24-bit RGB + 8-bit alpha
- Resolution: 300 DPI

**Data Format:** PNG image
**Size:** ~500 KB - 2 MB per asset
**Processing Time:** ~20-60 seconds (API dependent)

---

## Stage 5: Asset Validation

### Input: Generated Asset + Prompt

**Processing:**
```python
violations = validator.validate_image_asset('assets/generated/photo_mouse_01.png')
prompt_violations = validator.validate_prompt(original_prompt)
```

**Checks Performed:**
- Forbidden effects detection (gradients, soft shadows)
- Color distribution analysis
- Dimension verification
- Anachronistic term scanning

### Output: Validation Report

```python
{
    'asset': 'assets/generated/photo_mouse_01.png',
    'violations': [
        'Soft shadow detected at coordinates (320, 450)',
        'Gradient found in background region'
    ],
    'passed': False
}
```

**Data Format:** Python dictionary → JSON
**Size:** ~1 KB per report
**Action:** If violations exist, regenerate with adjusted prompt

---

## Stage 6: Composition

### Input: Layout YAML + All Assets

**Assets Loaded:**
- Manual assets: `assets/manual/*.png`
- Generated assets: `assets/generated/*.png`
- Font files: `assets/fonts/*.ttf`
- Texture maps: `assets/textures/*.png`

**Processing:**
```python
# Create base
canvas = compositor.create_base_canvas()

# Add each element
for element in layout['left_page']['elements']:
    asset = compositor.load_and_process_asset(element)
    canvas = compositor.composite_element(canvas, asset, element['position'])

# Render text
for text_block in layout['text_blocks']:
    text_img = compositor.render_text_block(text_block)
    canvas = compositor.composite_element(canvas, text_img, text_block['position'])
```

### Output: Composed Spread (Pre-Effects)

**File:** `temp/spread_04_05_composed.png`

**Properties:**
- Dimensions: 3400x2200 pixels
- Format: RGB (no alpha)
- Layers: Flattened
- Effects: None yet applied

**Data Format:** PNG image
**Size:** ~8-15 MB
**Processing Time:** ~3-8 seconds

---

## Stage 7: Post-Processing

### Input: Composed Spread

**Processing:**
```python
# Apply print artifacts
spread = post_processor.apply_cmyk_misregistration(spread)
spread = post_processor.apply_dot_gain(spread, gamma=0.95)
spread = post_processor.add_vignette(spread, opacity=0.15)
```

**Effects Applied:**

1. **CMYK Misregistration**
   - Shift red channel down 1px
   - Shift blue channel right 1px
   - Creates slight color fringing

2. **Dot Gain**
   - Apply gamma correction (0.95)
   - Reduce contrast slightly (0.95)
   - Simulates ink spread on uncoated paper

3. **Vignette**
   - Radial gradient from center
   - 15% opacity darkening at edges
   - Simulates photographed book

### Output: Final Spread with Effects

**File:** `output/spreads/spread_04_05.png`

**Properties:**
- Dimensions: 3400x2200 pixels
- Format: PNG
- Resolution: 300 DPI
- Effects: All applied

**Data Format:** PNG image
**Size:** ~10-20 MB
**Processing Time:** ~2-4 seconds

---

## Stage 8: Quality Assurance

### Input: Final Spread + Layout Config

**Processing:**
```python
qa_report = qa.check_spread_quality(spread_image)
```

**Checks Performed:**
- Spine intrusion detection
- Color balance verification
- Contrast measurement
- Readability assessment
- Binding hole alignment

### Output: QA Report

```python
{
    'spread_id': '04-05',
    'passed': True,
    'metrics': {
        'color_balance': 0.92,      # 0.0-1.0, higher is better
        'contrast_ratio': 7.2,       # WCAG standard, > 4.5 good
        'spine_clear': True,         # No intrusion detected
        'binding_aligned': True      # Holes properly positioned
    },
    'warnings': [],
    'timestamp': '2025-11-05T10:30:00Z'
}
```

**Data Format:** JSON
**Size:** ~2 KB per report
**Processing Time:** ~1-2 seconds

---

## Stage 9: Assembly

### Input: All Approved Spreads

**Files:**
- `output/spreads/spread_02_03.png`
- `output/spreads/spread_04_05.png`
- `output/spreads/spread_06_07.png`
- ... (n spreads)

**Processing:**
```python
spreads = sorted(Path('output/spreads').glob('spread_*.png'))
pdf = deploy.assemble_workbook(spreads)
```

**Assembly Steps:**
1. Sort spreads by page number
2. Convert each PNG to PDF page
3. Add metadata (title, author, date)
4. Add bookmarks for each spread
5. Embed fonts if text layers exist
6. Optimize PDF size

### Output: Final PDF Workbook

**File:** `output/Klutz_Workbook_v1.0.pdf`

**Properties:**
- Format: PDF 1.7
- Pages: n spreads (2 physical pages each)
- Resolution: 300 DPI
- Color space: RGB
- Compression: ZIP/Flate

**Data Format:** PDF
**Size:** ~50-150 MB (depends on spread count)
**Processing Time:** ~5-10 seconds for 20 spreads

---

## Data Size Summary

| Stage | Input Size | Output Size | Count |
|-------|-----------|-------------|-------|
| Layout YAML | - | ~3 KB | 1 per spread |
| Prompt Files | ~3 KB | ~2 KB | 5-15 per spread |
| Generated Assets | - | ~1 MB | 5-15 per spread |
| Validation Reports | ~1 MB | ~1 KB | 5-15 per spread |
| Composed Spread | ~10 MB | ~12 MB | 1 per spread |
| Final Spread | ~12 MB | ~15 MB | 1 per spread |
| PDF Workbook | ~300 MB | ~100 MB | 1 total |

**Total Storage per Spread:** ~50-100 MB (all intermediate files)
**Total Storage per Workbook:** ~2-3 GB (20 spreads)

---

## Processing Time Summary

| Stage | Time per Element | Time per Spread |
|-------|-----------------|-----------------|
| Prompt Generation | ~0.5s | ~5s (10 elements) |
| Gemini Refinement | ~3s | ~30s (10 elements) |
| Image Generation | ~30s | ~300s (10 elements) |
| Validation | ~2s | ~20s (10 elements) |
| Composition | - | ~5s |
| Post-Processing | - | ~3s |
| Quality Assurance | - | ~2s |
| **Total per Spread** | - | **~6 minutes** |
| **Batch (20 spreads)** | - | **~2 hours** |

**Optimization:** With parallel processing of independent spreads, batch time can be reduced to ~30 minutes on multi-core systems.

---

## Caching Strategy

### Prompt Cache

**Key:** MD5 hash of layout element config
**Value:** Generated XML prompt
**Hit Rate:** ~60% (elements reused across spreads)
**Savings:** ~2s per cache hit

### Asset Cache

**Key:** MD5 hash of refined prompt
**Value:** Generated PNG asset
**Hit Rate:** ~40% (similar elements)
**Savings:** ~30s per cache hit

### Composition Cache

**Key:** MD5 hash of layout YAML + asset hashes
**Value:** Composed spread (pre-effects)
**Hit Rate:** ~20% (iterations on same layout)
**Savings:** ~5s per cache hit

**Total Cache Savings:** ~30-40% reduction in regeneration time

---

## Error Propagation

### Error at Prompt Generation

**Impact:** Cannot generate assets for affected elements
**Recovery:** Fix YAML layout, regenerate prompts
**Propagation:** Stops at this stage

### Error at Image Generation

**Impact:** Missing asset for composition
**Recovery:** Regenerate with adjusted prompt or use placeholder
**Propagation:** Composition will fail if asset required

### Error at Validation

**Impact:** Asset flagged for regeneration
**Recovery:** Adjust prompt, regenerate asset
**Propagation:** Can proceed with warnings

### Error at Composition

**Impact:** Spread incomplete or incorrect
**Recovery:** Fix asset positions, regenerate composition
**Propagation:** Stops at this stage

### Error at Quality Assurance

**Impact:** Spread flagged for review
**Recovery:** Manual review and approval override
**Propagation:** Can proceed to assembly with approval

---

## Data Transformation Examples

### Example: Photo Element Data Flow

```
1. YAML Config:
   - id: "L_photo_mouse_01"
   - type: "graphic_photo_instructional"
   - position: [200, 300]

2. Generated Prompt:
   "A photograph of a beige Apple M0100 mouse..."

3. Refined Prompt:
   "A photograph taken from 45° angle showing a beige one-button
    Apple Macintosh M0100 mouse being used by a hand on a wooden
    desk, natural window lighting from left..."

4. Generated Image:
   assets/generated/photo_mouse_01.png
   800x600px, RGB+A, ~1.2 MB

5. Validated Image:
   ✓ No gradients detected
   ✓ Hard shadows only
   ✓ Period-accurate

6. Transformed Image:
   - Rotated 2° clockwise
   - 4px black border added
   - Hard shadow (3px offset)

7. Composited:
   Placed at (200, 300) on left page

8. Post-Processed:
   CMYK shift, dot gain, vignette applied

9. Final Output:
   Part of spread_04_05.png at (200, 300)
```

---

## Parallel Processing Flow

### Sequential vs Parallel

**Sequential (1 core):**
```
Spread 1 → Spread 2 → Spread 3 → ... → Spread 20
   6m        6m         6m              6m
Total: 120 minutes
```

**Parallel (8 cores):**
```
[Spread 1, Spread 2, Spread 3, Spread 4, Spread 5, Spread 6, Spread 7, Spread 8]
   6m        6m         6m        6m        6m        6m        6m        6m

[Spread 9, Spread 10, Spread 11, Spread 12, Spread 13, Spread 14, Spread 15, Spread 16]
   6m        6m          6m         6m         6m         6m         6m         6m

[Spread 17, Spread 18, Spread 19, Spread 20]
   6m         6m          6m          6m

Total: 18 minutes (3 batches × 6m)
```

**Speedup:** ~6.7x with 8 cores

---

## See Also

- [system-overview.md](system-overview.md) - High-level architecture
- [directory-structure.md](directory-structure.md) - File organization
- [../api/](../api/) - API documentation
