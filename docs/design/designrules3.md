Core Mandate: The Hypothetical 1996 Klutz Computer Graphics Workbook
As an expert-level prompt engineer, your task is to transform source documents into hyper-specific, few-shot prompts for nano-banana. This document is a technical specification for a two-stage, tag-based image generation workflow.

The objective is to algorithmically generate a hypothetical artifact: a two-page spread from a spiral-bound computer graphics workbook published by Klutz Press in 1996. Since research confirms Klutz published no technology books in this period, our goal is to meticulously apply their authentic design philosophy to a subject they never covered.

The final output is a precisely defined, densely layered "organized chaos" that prioritizes hands-on learning and tactile experience over visual spectacle. All rules are mandatory.

The Two-Stage Workflow
Generation is a sequential process. Each stage has a distinct objective.

Stage 1: Layout, Graphics, and Headlines
The first prompt renders the entire visual scene without body text. This includes the paper, background elements, all graphics, photos, doodles, and text containers. Headlines and titles are rendered in this stage. Every element is assigned a unique tag_id and is defined by a detailed Element Definition Block.

Stage 2: Typographic In-painting
The second prompt targets the blank text containers generated in Stage 1, using their tag_id to fill them with body text. This stage is focused entirely on achieving perfect, legible, and stylistically correct typography.

The Canvas: Physical & Digital Specifications
Authentic Klutz Press Physicality
Paper Stock: Interior pages must use 60-80lb uncoated text paper. The prompt must specify one of the following appearances:

Bright White Matte (#FFFFFF)

Aged Newsprint (#F8F3E5)

Resolution: 3400x2200 pixels.

Binding & Margins: The layout must adhere to Klutz's signature spiral binding requirements.

The black plastic coil binding must be a celebrated visual element.

Spine Margin: 0.77" total (0.5" design margin + 0.27" for holes).

Other Margins: 0.5" on the three non-spine sides.

Hole Specifications: 0.19" diameter round holes with 0.06" spacing (4:1 pitch).

Digital Environment Simulation
Any simulation of a computer environment must fully and accurately resemble Apple System 6 for the Macintosh Plus. Simulating Windows is forbidden.

Mandatory Color Systems
Klutz employed a high-contrast, primary-plus-secondary color strategy with warm, approachable combinations, explicitly rejecting the "acidic, saturated colors" of competitors.

IMPORTANT: Modern color gradients and ANY COMMON DESIGN AESTHETIC POST-1997 ARE STRICTLY FORBIDDEN.

System 1: Authentic Klutz Palette (Primary Choice)

Description: Based on their core 1996 product line, this system uses bold primary and secondary colors plus black and white.

Colors: Red, Blue, Yellow, Green, Orange, Purple.

System 2: Hypothetical "Hypercolor" Variants (Secondary Choice)

Description: These palettes from the original designrules.md represent a more commercial, Scholastic-inspired aesthetic for creative flexibility.

Palettes: "Nickelodeon Splat," "Retro Pop," "Pastel Paradise".

Additional Approved Colors: Hot Magenta (#FF00FF), Electric Cyan (#00FFFF), Screaming Yellow (#FFFF00), Radical Teal (#008080), Deep Purple (#800080), Gray (#808080).

Fontography: Prescriptive & Authentic Typography
Klutz typography prioritized clarity and accessibility for young readers.

Body Text (14pt-18pt): Must use a humanist sans-serif font like Helvetica or Frutiger. Leading must be generous (16-22pt). Must use simplified single-story 'a' and 'g' characters.

Headings/Titles: Chicago or Charcoal, for the hypothetical computer-book feel. Must use mixed type sizes for visual hierarchy.

Accent/Callouts: Monaco or Courier New. Emphasis should be achieved with bold weights and increased point sizes rather than decorative typefaces.

The Element Definition Block & Tagging System
Every component on the page is an "Element" and must be defined using the standardized markdown block below.

Markdown

### Element: [Descriptive Name, e.g., "Main Title Graphic"]
- **tag_id**: `[unique_string_identifier, e.g., headline_main_01]`
- **type**: `[text_headline | text_body_container | graphic_photo_instructional | graphic_pixelart | graphic_doodle | container_featurebox | graphic_gui_recreation]`
- **geometry**:
    - **position_xy**: `(x, y)`
    - **dimensions_wh**: `(width, height)`
    - **rotation_deg**: `[number]`
- **appearance**:
    - **[Property]**: `[Value]`
- **positive_prompt**: `[A hyper-specific, evocative description of the element's visual content and style.]`
- **negative_prompt**: `[A targeted list of failures to avoid for THIS SPECIFIC element.]`
Layout & Element Specifications: The "Organized Chaos" Formula
Layouts must appear chaotic but follow underlying organizational principles, featuring multiple visual entry points and designated "activity zones".

type: graphic_photo_instructional (Primary Visual Element)

Description: Following Klutz's "fully photographic how-to" format, the primary method of instruction must be through sequential, well-lit photographs showing hand positions and actions (e.g., using a mouse, pressing keys). Illustrations are secondary.

Required Properties: subject_description, camera_angle, lighting_style: clear_and_well-lit, border: (color, width_px).

type: container_featurebox or sidebar

Description: Used for supplementary information.

Required Properties: background_texture: subtle_pattern, border: chunky_solid-color_4-6px, shadow: hard-edged_offset_3-4px_no-blur.

type: text_body_container

Description: An empty container for Stage 2 text, designed with generous white space around it to ensure readability when placed on busy backgrounds.

Required Properties: text_content: "", background_color, border, shadow.

type: graphic_pixelart or graphic_gui_recreation

Description: The necessary visual assets for a computer graphics topic. Pixel art should resemble 8 and 16-bit console graphics. GUI recreations of Aseprite are required where appropriate.

Required Properties: subject_description, pixel_palette, magnification.

Stage 2 type: text_body

Description: The typographic fill for a text_body_container.

Required Properties: text_content, font_name: Helvetica, font_size_pt: 14-18, font_color, leading_pt: 16-22, justification.

Positive Prompt: Must instruct the model to use clear contrast ratios to maintain readability.
