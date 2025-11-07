# config/master_config.yaml
# Master configuration for 1996 Klutz Computer Graphics Workbook

project:
  name: "Klutz Press Computer Graphics Workbook"
  subtitle: "Learn Pixel Art the Klutz Way!"
  year: 1996
  pages: 48
  binding: "spiral"
  format: "landscape"

technical_specifications:
  canvas:
    dimensions: [3400, 2200]
    dpi: 300
    color_space: "sRGB"
    bit_depth: 24

  margins:
    top: 150
    bottom: 150
    outer_left: 150
    outer_right: 150
    spine_margin: 231  # Total spine width: 462px

  safe_zones:
    left_page:
      x_range: [150, 1469]
      y_range: [150, 2050]
    right_page:
      x_range: [1931, 3250]
      y_range: [150, 2050]

  spine_specifications:
    center_x: 1700
    width: 462
    dead_zone: [1469, 1931]
    binding_holes:
      pitch: "4:1"
      diameter: 57
      spacing: 18
      count: 29

color_specifications:
  primary_palette:
    red: "#FF0000"
    blue: "#0000FF"
    yellow: "#FFFF00"
    green: "#00FF00"
    orange: "#FFA500"
    purple: "#800080"
    black: "#000000"
    white: "#FFFFFF"

  accent_palette:
    nickelodeon_orange: "#F57D0D"
    nickelodeon_slime: "#C4D600"
    goosebumps_acid: "#95C120"
    goosebumps_toxic: "#68EA34"

  usage_rules:
    primary_minimum: 0.70
    nickelodeon_maximum: 0.20
    goosebumps_maximum: 0.10

  paper_colors:
    bright_white: "#FFFFFF"
    aged_newsprint: "#F8F3E5"
    recycled_gray: "#F0F0E8"

typography_specifications:
  body_text:
    fonts: ["Helvetica", "Frutiger"]
    sizes: [14, 15, 16, 17, 18]
    leading_multiplier: 1.4
    color: "#000000"
    simplified_glyphs: true

  headlines:
    fonts: ["Chicago", "Charcoal"]
    sizes: [24, 36, 48, 60, 72]
    style: "bitmap_no_antialiasing"
    color: "#000000"

  accent_text:
    fonts: ["Monaco", "Courier New"]
    sizes: [9, 10, 12]
    usage: "code_and_technical"

  special_effects:
    embossed:
      depth: "15-25 microns"
      style: "blind_emboss"
      no_ink: true

    dripping:
      fonts: ["custom_slime"]
      colors: ["#C4D600"]
      usage: "special_headlines_only"

element_specifications:
  rotation_limits:
    text_blocks: 5
    containers: 15
    photos: 10
    decorative: 30

  shadow_specifications:
    type: "hard_edge_only"
    offset: [3, 3]
    blur: 0
    color: "#000000"
    opacity: 1.0

  border_specifications:
    standard_widths: [2, 3, 4, 6]
    style: "solid"
    colors: ["#000000", "#FF0000", "#0000FF", "#FF6600"]

print_simulation:
  cmyk_misregistration:
    cyan: [0, 0]
    magenta: [1, 0]
    yellow: [0, -1]
    black: [0, 0]

  dot_gain:
    uncoated_paper: 0.23
    gamma_adjustment: 0.95

  paper_texture:
    type: "uncoated_newsprint"
    opacity: 0.08
    grain_direction: "horizontal"

  physical_effects:
    vignette_opacity: 0.15
    spine_shadow_opacity: 0.20
    page_curl_size: 100

photographic_specifications:
  film_stock: "Kodak Gold 400"
  alternative: "Fuji Superia 400"

  characteristics:
    grain_index: 39
    color_profile: "warm_highlights_neutral_midtones"
    typical_settings:
      iso: 400
      aperture: "f/8-f/16"
      shutter: "1/60-1/250"

  lighting_setup:
    key_light:
      type: "softbox"
      size: "24x36 inches"
      position: "45° left, 30° elevation"
      distance: "24 inches"

    fill_light:
      type: "reflector"
      position: "60° right"
      ratio: "1:2"

validation_settings:
  strict_mode: true

  forbidden_terms:
    - "gradient"
    - "web 2.0"
    - "UX"
    - "mobile"
    - "responsive"
    - "modern"
    - "minimal"
    - "clean"
    - "sleek"

  required_elements:
    - spiral_binding
    - paper_texture
    - cmyk_misregistration

  quality_checks:
    - color_distribution
    - spine_clearance
    - text_legibility
    - period_authenticity
    - rotation_compliance

file_organization:
  naming_convention: "[page]_[type]_[description]_[index]"

  directory_structure:
    assets: "assets/generated/"
    prompts: "prompts/components/"
    layouts: "config/layouts/"
    output: "output/spreads/"
    validation: "output/validation/"

  version_control:
    track_prompts: true
    track_assets: true
    track_layouts: true

output_specifications:
  file_format: "PNG"
  compression: "lossless"
  metadata:
    include_dpi: true
    include_color_profile: true
    include_creation_date: true

  deliverables:
    raw_composites: true
    processed_spreads: true
    individual_assets: true
    validation_reports: true
