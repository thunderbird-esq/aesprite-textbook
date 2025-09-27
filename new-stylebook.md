# Stylebook Version 4

## 1.0 Guiding Principles & The Golden Rule

This document provides the complete, unified technical and creative framework for generating all assets for the workbook. It is the single source of truth.

**The Golden Rule of Hyper-Specificity:** This project's success hinges on translating creative goals into mathematically precise, unambiguous instructions for the generative AI ("nano-banana"). All prompts must be literal, quantitative, and exhaustive. Avoid all subjective terms in favor of objective, measurable values.

* **Success:** A solid red (`#FF0000`) border, 4 pixels wide, with a hard-edged drop shadow in black (`#000000`) offset by x=3, y=3 pixels, with 0 pixel blur.
* **Failure:** A nice, thick red border with a cool shadow.

## 2.0 The Brand & Content Bible: The "Soul" of the Project

### 2.1 The Klutz Writing Style: The Technical Tightrope

The written copy must balance the authentic Klutz voice with accurate technical detail, as defined in `klutz-press-design.md`.

**Klutz Voice Profile:** Humorous, self-deprecating, encouraging, enthusiastic, and uses puns. Addresses the reader directly as "you."

* **Success:** "Time to choose a color! Don't worry, you can't mess this up. (Okay, maybe you can, but that's what the Undo button is for!)"
* **Failure:** "The user must now select a color from the palette interface to proceed with the operation."

**The Technical Tightrope:** Introduce technical terms with a simple, funny analogy first, then provide the correct, detailed definition. The content must align with the provided Aseprite tutorial modules.

* **Success:** "Okay, let's talk about Indexed Color. Imagine you only have a 16-pack of crayons to color a giant masterpiece. You have to be clever about how you use them, right? That's Indexed Color! To be technical, converting to Indexed Mode limits your entire image to a specific, fixed palette of colors (like 16 or 32). This is the secret to getting that classic video game look and makes changing all the reds in your picture a total no-brainer."
* **Failure:** "Indexed Color Mode is a method of managing digital image data that limits the image's colors to a predefined palette."

**Lexicon:**
* **Approved "Klutz-isms":** "Awesome," "Radical," "Complete Klutz," "Brain-dead simple," "No-brainer," "Bingo!"
* **Forbidden Words:** "Utilize," "thus," "therefore," "synergy," "leverage," "streamline."

### 2.2 The Physical "Thing": The Floppy Disk & Stickers

**Rationale:** As per `klutz-press-design.md`, a core Klutz philosophy was the inclusion of physical tools. This workbook must simulate this.

**Item Definition:** The workbook includes two items held in a die-cut holder:
* A 3.5" 1.44MB Floppy Disk: Beige color, containing "Klutz Paint v1.0" software (a hypothetical, simplified version of Aseprite).
* A 4"x4" Sheet of Vinyl Stickers: Featuring pixel monster sprites taught in the book's tutorials.

* **Success:** The layout includes a `container_diecut_holder` element on page 2 or 3 that is visually convincing.
* **Failure:** The book makes no visual reference to its included physical components.

## 3.0 The Four-Stage Workflow: Detailed Breakdown

### Stage 0: Layout Pre-flight
**Objective:** To prevent text overflow errors and wasted rendering time by analyzing text fit before any images are generated.

**Technical Implementation:**
* A script ingests the complete layout plan, including all `text_body_container` dimensions and the final `text_content` for each.
* Using a font metrics library (e.g., FreeType), the script calculates the estimated rendered bounding box of the `text_content` using the specified `font_name`, `font_size_pt`, and `leading_pt`.
* It compares the estimated text area to the target container's `dimensions_wh` (minus its `internal_padding_px`).
* If the estimated text area exceeds 90% of the container's padded area, the script flags a "High Risk Overflow" warning for the engineer, who can then choose to enlarge the container or edit the text before committing to the Stage 1 render.

* **Success:** The script flags that the text for `L_textcontainer_intro_01` is 95% of the container size, allowing the engineer to resize the box before rendering.
* **Failure:** The engineer proceeds directly to Stage 1, only to find in Stage 2 that the text doesn't fit, wasting time and resources.

### Stage 1: Composition & Layout
**Objective:** To generate a single, high-resolution image file of the entire two-page spread, fully rendered with all visual elements except for the body text.

**Technical Implementation:**
* The prompt engineer creates a complete list of Element Definition Blocks for all visual components, adhering to the layout templates and composition rules.
* This list is fed to the AI ("nano-banana") to generate a single 3400x2200 pixel `.png` image.
* `text_body_container` elements are rendered as visually defined boxes (with borders, backgrounds, etc.) but are filled with a solid, unique color (e.g., `#FF00FF`) to serve as a perfect mask. The underlying paper grain and texture are rendered inside these containers.

* **Success:** A single, high-fidelity image is produced where all body text areas are well-defined, empty, and ready for Stage 2.
* **Failure:** The AI hallucinates text in the containers, or renders the containers without the necessary underlying paper texture.

### Stage 2: Typographic In-painting
**Objective:** To fill the empty text containers with stylistically perfect, brand-correct typography that appears naturally integrated with the paper.

**Technical Implementation:**
* **Content Sanitization:** The final `text_content` is scanned. Potentially style-influencing words are modified for the AI prompt (e.g., "photorealistic" becomes "highly detailed") to prevent the AI from breaking typographic character.
* For each `text_body_container`, an in-painting job is initiated. The AI is provided with:
    * The full Stage 1 image.
    * A mask generated from the `text_body_container`'s area (minus its `internal_padding_px`).
    * The sanitized `text_content`.
    * A `typographic_reference_image` showing key letterforms.
    * A highly specific prompt demanding adherence to the font, size, leading, color, and texture of the underlying paper.

* **Success:** Text is rendered cleanly inside the container's padded area, matching the paper grain and specified font characteristics perfectly.
* **Failure:** Text bleeds outside the container, is rendered in the wrong font, or appears flat and "pasted on" without matching the paper texture.

### Stage 3: Post-Processing & Unification
**Objective:** To apply a final layer of global, quantified effects that simulate real-world printing and handling, unifying all generated elements into a believable physical artifact.

**Technical Implementation:** The complete image from Stage 2 is processed through a non-subjective, automated filter chain in a specific order:
1.  **Texture Unification:** A single, unbroken `subtle_uncoated_paper_grain` texture is overlaid at 8% opacity.
2.  **Printing Artifacts:**
    * **CMYK Misregistration:** The Magenta color channel is shifted horizontally by +1 pixel. The Yellow channel is shifted vertically by -1 pixel.
    * **Dot Gain:** A Levels filter adjusts the mid-tones (gamma) from 1.0 to 0.95.
3.  **Lighting Unification:**
    * **Vignette:** A circular black vignette is applied (15% opacity, 400-pixel feather).
    * **Spine Shadow:** A linear shadow gradient is applied across the spine area (20% opacity at the center).

* **Success:** The final image has faint, consistent paper texture, tiny color halos on printed edges, slightly softer photos, and realistic lighting, making it feel like a photograph of a real book.
* **Failure:** The effects are too strong, making the image look like a cheap filter was applied, or they are not applied, leaving the image looking sterile and digital.

## 4.0 Design Ethos & Aesthetic Hierarchy: Detailed Rationale

### Klutz is the Foundation (70% Rule)
**Rationale:** The core mandate is to create a Klutz book. As per `klutz-press-design.md`, this means prioritizing a "fully photographic how-to" format, an "imperfection aesthetic," and "organized chaos." The design must feel accessible and encourage hands-on learning over mere observation.

**Technical Implementation:** Layouts are built from Klutz-first templates. The majority of the color palette is Klutz primary colors. The primary method of instruction is always `graphic_photo_instructional`.

### Nickelodeon is the Energy (Framing Rule)
**Rationale:** As per `nickelodeon-goosebumps-design.md`, Nickelodeon's 1990s identity was "anti-establishment," using a "Flexi-Logo" system and a signature Pantone Orange 021 C designed to "clash with everything." This high-energy aesthetic is co-opted to make the "tech" subject matter feel exciting and rebellious.

**Technical Implementation:** Nickelodeon Orange is used for energetic, frame-like `graphic_splat_container` elements that break the grid. The typography for these elements can reference Balloon Extra Bold for single, impactful words.

### Goosebumps is the Texture & Theme (Special Effect Rule)
**Rationale:** As per `nickelodeon-goosebumps-design.md`, Goosebumps covers used "blind embossing" to create a tactile, "bumpy" feel and "acidic, saturated colors" for thematic effect. This is leveraged to add literal texture and to theme specific tutorial content (e.g., creating monsters).

**Technical Implementation:** The `container_embossed_featurebox` directly simulates the tactile embossing. "Acid" greens are reserved exclusively for the `pixel_palette` of monster sprites or "glitch" effect graphics. Specialty headlines can use a "dripping slime" effect.

## 5.0 The Canvas: Pixel-Specific Grid & Coordinate System

**Rationale:** To create a believable spiral-bound book, the physical constraints of printing and binding must be digitally simulated with mathematical precision. These dimensions are derived from the 0.77" spine margin and 0.5" outer margins specified in `klutz-press-design.md`, converted to pixels at a print-quality resolution of 300 DPI.

**Technical Implementation:**
* **Total Canvas Dimensions:** (3400, 2200)
* **Margins:** 150 pixels on top, bottom, and outer left/right edges.
* **Spine & Binding Area (The Dead Zone):** Total width of 462 pixels centered at x=1700. No content may bleed into this area.
* **Safe Zones:**
    * Left Page: `position_xy`: (150, 150), `dimensions_wh`: (1319, 1900)
    * Right Page: `position_xy`: (1931, 150), `dimensions_wh`: (1319, 1900)

* **Success:** All core content (text, important parts of photos) is contained within the Safe Zones. The area marked as the Spine is left clear for the `graphic_spiral_binding` element.
* **Failure:** A headline is placed at x=1600, causing it to be partially obscured by the rendered binding holes.

## 6.0 Tagging, Metadata, & Pre-flight Verification

**Rationale:** A complex, multi-stage generative workflow is prone to cascading failures from simple errors. A strict, machine-readable naming convention and an automated verification step are essential for a reliable production pipeline.

**Technical Implementation:**
* **Naming Convention:** All `tag_ids` must strictly follow the schema: `[page]_[type]_[description]_[index]`.
* **Stage 2 Pre-flight:** A mandatory script runs before Stage 2. It parses the Stage 1 output metadata and the Stage 2 plan, cross-referencing every `target_tag_id`. If a tag is missing, misspelled, or duplicated, the script halts and outputs a specific error (e.g., `ERROR: target_tag_id 'R_photo_mousclick_01' not found. Did you mean 'R_photo_mouseclick_01'?`).

* **Success:** A tag is misspelled as `L_featurebox_paltip_O1` (with an "O" instead of "0"). The pre-flight script catches the error and halts, preventing a failed render.
* **Failure:** The script is not run, and the AI spends resources attempting a Stage 2 in-paint that fails, leaving a blank box in the final output.

## 7.0 Color Systems & Usage Rules

**Rationale:** The color strategy is a direct implementation of the aesthetic hierarchy. The Klutz palette provides a warm, accessible base, while the Nickelodeon and Goosebumps colors are used as high-impact accents, preventing the "acidic" colors from overwhelming the friendly Klutz feel, as warned against in `klutz-press-design.md`.

**Technical Implementation:**
* **Primary Palette (Klutz Base - ~70-80% usage):** Red, Blue, Yellow, Green, Orange, Purple, Black, White. Used for backgrounds, core containers, and instructional elements.
* **Accent Palette (Klutz-Tech "Zine" - ~20-30% usage):**
    * **Nickelodeon Orange (`#F57D0D`):** Reserved for `type: graphic_splat_container`.
    * **Goosebumps "Acid" Greens (`#95C120`, `#68EA34`):** Reserved for thematic graphics like monster sprites.
    * **Nickelodeon Slime Green (`#C4D600`):** Reserved for "slime" effects.

* **Success:** The overall page feels bright and colorful in the Klutz style, with a pop of vibrant orange from a splat that draws attention to a key screenshot.
* **Failure:** The entire page background is set to Goosebumps Acid Green, making it visually fatiguing and off-brand.

## 8.0 Fontography & Typographic Rules

**Rationale:** The font choices are derived directly from the source documents. Klutz used humanist sans-serifs for readability. Chicago and Charcoal were the system fonts for Apple computers of the era. Monaco/Courier New evokes the feeling of code or technical text.

**Technical Implementation:**
* **Body Text:** 14-18pt Helvetica or Frutiger with 16-22pt leading. Single-story 'a'/'g' are mandatory.
* **Headings:** 24-72pt Chicago or Charcoal, rendered as bitmapped graphics (non-anti-aliased).
* **Accent/Code:** 12pt Monaco or Courier New.

* **Success:** Body text is clear, legible, and friendly. Headings have a pixel-perfect, retro-tech feel.
* **Failure:** The body text is rendered in the Chicago font, making it difficult to read in long paragraphs.

## 9.0 The Element Definition Block

**Rationale:** This structured block is the core of the entire system. It forces the translation of every creative idea into a machine-readable, technically precise format required by the Golden Rule.

**Technical Implementation:** All fields must be filled. No subjective language.

```
### Element: [Descriptive Name]
- **tag_id**: `[page]_[type]_[description]_[index]`
- **type**: `[element_type]`
- **geometry**: ...
- **appearance**: ...
- **positive_prompt**: ...
- **negative_prompt**: ...
```

* **Success:** Every property is filled with a specific, quantitative value. Positive/negative prompts are detailed and technical.
* **Failure:** Properties contain subjective terms; prompts are vague.

## 10.0 Book Pacing & Layout Templates

**Rationale:** A real book has a deliberate flow and recurring structures. These templates and cadence rules prevent the workbook from feeling like a random collection of pages, ensuring a cohesive reading experience.

**Technical Implementation:** All two-page spreads must be based on one of the following templates, and element usage must follow the cadence rules.
* **Template A: "The Focus Photo":** Left page is dominated by a single, large `graphic_photo_instructional`. Right page contains the main text block.
* **Template B: "The Workshop":** A dense mix of smaller instructional photos, text containers, and GUI recreations.
* **Template C: "The Showcase":** Right page is a full-bleed showcase for a large piece of `graphic_pixelart`.

**Element Cadence:** One `embossed_featurebox` per chapter. `container_diecut_holder` on pages 2-3 only.

* **Success:** Chapter 1 uses Template A for a simple introduction. Chapter 2 uses Template B for a complex tutorial. The embossed box appears on page 9 and not again until page 17.
* **Failure:** Every page is a chaotic mess with no underlying structure, or an embossed box appears on three consecutive pages.

---

## 11.0 Global Composition Principles

**Rationale:** These rules codify the "organized chaos" philosophy. They provide a quantitative framework for achieving a dynamic, hand-made feel without sacrificing clarity and usability.

**Technical Implementation:**
* **Layering is Mandatory:** Elements must overlap.
* **The 60/40 Chaos Ratio:** At least 60% of the page's content area must be occupied by unrotated instructional containers.
* **Rotation Containment:** Rotation is not cumulative within nested elements.
* **Semantic Hotspots:** No decorative elements may obscure a photo's defined hotspot.
* **Readability Moats:** Every text container must be surrounded by 50-100 pixels of clear space.

* **Success:** The main text block and GUI recreation are perfectly level, while photos and sidebars are playfully tilted, and a doodle arrow is layered on top of the corner of a photograph.
* **Failure:** The main text block is rotated 10 degrees, making it difficult to read. A large "ZAP!" doodle is placed directly over the character's face in a photo.

---

## 12.0 Detailed Element Specifications

**Rationale:** This section provides the exhaustive, pre-written prompt components for every possible element, ensuring maximum consistency and adherence to the design system.

**Technical Implementation:** The prompt engineer assembles prompts using these tested and approved blocks.

#### type: `container_diecut_holder`
* **positive_prompt:** A photorealistic rendering of a 3.7-inch square, die-cut depression in the heavy card stock of the page. The depression has a hard-edged shadow suggesting a depth of 4mm. A semicircular thumb-hole is cut on the right side. The texture of the paper is visible inside the depression. A beige 3.5" floppy disk with a simple black and white label reading 'Klutz Paint' is visible inside.
* **negative_prompt:** sticker, printed image, no depth, soft shadow, floating disk, unrealistic

#### type: `graphic_spiral_binding` (Mandatory)
* **positive_prompt:** A photorealistic rendering of black plastic spiral binding coils seen through a series of clean, die-cut circular holes (57px diameter, 18px spacing). Each hole has a crisp, hard-edged inner shadow on one side to simulate paper thickness.
* **negative_prompt:** misaligned holes, torn paper, rust, metal binding, soft shadows

#### type: `container_embossed_featurebox`
* **positive_prompt:** The words "[TEXT]" are blind-embossed into the container, creating a raised, bumpy, 3D effect with hard-edged highlights and shadows as if pressed from behind the paper. No ink or foil on the embossed letters.
* **negative_prompt:** photoshop bevel filter, soft inner glow, letterpress ink, metallic

#### type: `graphic_photo_instructional`
* **positive_prompt:** A clean, well-lit, high-angle photograph shot on 35mm film of a kid's hand using a beige Apple Macintosh Plus mouse (model M0100). The photo is clear and in sharp focus. The background is a simple, solid-colored mousepad.
* **negative_prompt:** blurry, dramatic hollywood lighting, dark shadows, modern optical mouse, motion blur, film grain

#### type: `graphic_broadcast_media`
* **positive_prompt:** A vibrant graphic emulating the 1996 Quantel Paintbox look. Features hard-edged digital airbrushing, visible aliasing on curved edges, and subtle but noticeable color banding in gradients.
* **negative_prompt:** photorealistic, vector art, smooth gradients, anti-aliasing, soft focus

#### type: `graphic_gui_recreation`
* **positive_prompt:** A perfect, pixel-for-pixel recreation of a MacPaint window from Apple System 6. Strictly monochrome black and white, using only stippled patterns to simulate gray. UI elements use the bitmapped Chicago font.
* **negative_prompt:** color, grayscale, anti-aliasing, modern UI, smooth fonts, drop shadows

---

## 13.0 Stage-Specific Workflow Execution

**Rationale:** This section provides a detailed, step-by-step checklist for the human operator and the automation scripts, ensuring the complex four-stage workflow is executed correctly and consistently every time.

**Technical Implementation:** Follow the detailed breakdown of each stage as defined in Section 3.0. This includes running the pre-flight scripts, using unique colors as masks in Stage 1, applying content sanitization in Stage 2, and using the exact quantified values for the global filters in Stage 3.

* **Success:** The final output is a believable, high-quality artifact that precisely matches the specifications.
* **Failure:** Any deviation from the proscribed workflow, such as applying Stage 3 effects manually or skipping the Stage 0 pre-flight, resulting in an inconsistent or flawed output.
