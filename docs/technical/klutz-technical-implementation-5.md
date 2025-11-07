# config/layouts/spread_04_05.yaml
# Complete layout specification for pages 4-5: Introduction to Pixel Art

spread_info:
  number: "04-05"
  title: "Pixel Perfect! Making Your First Sprite"
  template: "workshop_layout"
  canvas: "aged_newsprint"

global_settings:
  color_distribution:
    klutz_primary: 0.72
    nickelodeon_accent: 0.20
    goosebumps_theme: 0.08

  texture_settings:
    paper_grain: 0.08
    emboss_depth: 20  # microns

  print_settings:
    cmyk_misregistration: true
    dot_gain: 0.95
    vignette_opacity: 0.15

left_page:
  elements:
    - id: "L_headline_pixelart_01"
      type: "text_headline"
      position: [200, 180]
      dimensions: [800, 100]
      rotation: -3
      content: "PIXEL PERFECT!"
      font: "Chicago"
      size: 48
      color: "#000000"
      border: "none"
      shadow:
        offset_x: 2
        offset_y: 2
        color: "#808080"

    - id: "L_photo_mouse_01"
      type: "graphic_photo_instructional"
      filename: "photo_mouse_hand_01.png"
      position: [250, 300]
      dimensions: [600, 450]
      rotation: 2
      border: "4px solid #FF6600"
      shadow:
        offset_x: 3
        offset_y: 3
        color: "#000000"
      subject: "child hand on Apple M0100 mouse"
      camera:
        lens: "100mm macro"
        aperture: "f/11"
        shutter: "1/125"
      lighting:
        key: "45 degrees left, 30 degrees up"
        fill: "60 degrees right, reflector"

    - id: "L_textcontainer_intro_01"
      type: "container_featurebox"
      position: [180, 800]
      dimensions: [900, 400]
      rotation: -1
      background: "#FFD700"
      border: "4px solid black"
      internal_padding: 20
      text_content: |
        Time to make some pixel art! Remember those
        awesome Nintendo characters? They're just
        colored squares arranged in a grid. You're
        going to learn the same tricks the pros use,
        but way easier because you're using Aseprite
        instead of typing mysterious code!

        First, let's set up your workspace. Move your
        mouse (that beige thing in the photo above)
        and click on the color palette. Don't worry
        if you mess up - that's what Undo is for!
      font: "Helvetica"
      font_size: 16
      leading: 22
      color: "#000000"
      simplified_glyphs: true

    - id: "L_splat_tip_01"
      type: "graphic_splat_container"
      position: [950, 650]
      dimensions: [300, 200]
      rotation: 15
      color: "#F57D0D"
      content: "PRO TIP!"
      content_font: "Balloon_ExtraBold"
      content_size: 24
      content_color: "#FFFFFF"

    - id: "L_doodle_arrow_01"
      type: "graphic_doodle"
      position: [850, 750]
      dimensions: [150, 100]
      rotation: -25
      doodle_type: "curved_arrow"
      points_to: "L_photo_mouse_01"
      line_weight: 4
      color: "#000000"

    - id: "L_embossed_remember_01"
      type: "container_embossed_featurebox"
      position: [200, 1300]
      dimensions: [800, 200]
      rotation: 0
      background: "#F8F3E5"
      embossed_text: "REMEMBER!"
      emboss_depth: 20
      border: "2px solid #808080"
      content: "Save your work every 5 minutes!"
      content_position: "below_emboss"

right_page:
  elements:
    - id: "R_gui_aseprite_01"
      type: "graphic_gui_recreation"
      position: [1950, 200]
      dimensions: [1200, 800]
      rotation: 0
      software: "Aseprite"
      interface_elements:
        - "color_picker"
        - "tool_palette"
        - "canvas_grid"
      border: "1px solid black"

    - id: "R_pixelart_mario_01"
      type: "graphic_pixelart"
      position: [2100, 1100]
      dimensions: [400, 400]
      rotation: -5
      magnification: 8
      base_resolution: [32, 32]
      palette: "NES_limited"
      subject: "simple Mario-like character"
      colors:
        - "#000000"  # Black (outline)
        - "#FFFFFF"  # White (eyes)
        - "#FF0000"  # Red (hat, shirt)
        - "#0000FF"  # Blue (overalls)
        - "#FDB5A4"  # Peach (skin)
        - "#8B4513"  # Brown (shoes, hair)
      border: "2px solid black"

    - id: "R_textcontainer_steps_01"
      type: "container_featurebox"
      position: [2050, 1550]
      dimensions: [1000, 500]
      rotation: 1
      background: "#E6F3FF"
      border: "4px solid #0000FF"
      text_content: |
        STEPS TO PIXEL GREATNESS:
        1. Pick a color from the palette
        2. Click the pencil tool (one pixel at a time!)
        3. Draw your outline first (pros always do this)
        4. Fill in the colors with the paint bucket
        5. Add shading with darker versions of each color

        Start with something simple like a mushroom or
        a ghost. Once you get the hang of it, try making
        your own video game character!
      font: "Helvetica"
      font_size: 15
      leading: 20
      list_style: "numbered"
      list_indent: 30

    - id: "R_photo_screen_01"
      type: "graphic_photo_instructional"
      position: [2700, 300]
      dimensions: [500, 375]
      rotation: -3
      subject: "CRT monitor showing pixel art"
      border: "3px solid #808080"
      film_effect: "Kodak_Gold_400"

global_elements:
  - id: "spiral_binding"
    type: "graphic_spiral_binding"
    position: [1469, 0]
    dimensions: [462, 2200]
    specifications:
      pitch: "4:1"
      holes: 29
      hole_diameter: 57
      hole_spacing: 18
      coil_color: "#141414"
      coil_thickness: 8
      shadow_depth: 3

validation_rules:
  enforce_safe_zones: true
  check_spine_clearance: true
  validate_color_ratios: true
  maximum_element_overlap: 0.20
  minimum_text_contrast: 4.5
