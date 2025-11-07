# Module 3: Platform Constraints & Technical Requirements

## Session 3.1: GBStudio Requirements Deep Dive

### Understanding Game Boy Hardware

The Game Boy's 1989 hardware defines strict constraints that create the characteristic aesthetic. Understanding these limitations transforms them from obstacles into creative guides.

**Core Specifications:**
- CPU: 8-bit Sharp LR35902 at 4.19 MHz
- RAM: 8KB (plus 8KB video RAM)
- Resolution: 160×144 pixels
- Colors: 4 shades of green (original)
- Sprites: 40 total, 10 per scanline maximum

### The Four-Color Reality

GBStudio enforces the original DMG (Dot Matrix Game) palette:

**Exact Color Values:**
```
Color 0 (Lightest): #9BBD0F
Color 1 (Light):    #8BAC0F
Color 2 (Dark):     #306850
Color 3 (Darkest):  #0F380F
```

**Critical Distinction: Sprites vs Backgrounds**

*Background Palette:*
- Can use all 4 colors
- Color 2 (#306850) available
- More flexibility for shading

*Sprite Palette:*
- Only 3 colors + transparency
- Cannot use Color 2 (#306850)
- Color 0 becomes transparent
- More limited shading options

This means sprites appear "lighter" than backgrounds, creating natural separation.

### Sprite Size Mathematics

**Individual Sprite Constraints:**
- Minimum: 8×8 pixels (1 tile)
- Maximum: 8×16 pixels (2 tiles, vertically stacked)
- No other sizes possible in hardware

**Actor Sprite Combinations:**
GBStudio combines hardware sprites for larger characters:

*16×16 Actor (Most Common):*
- Uses 4 hardware sprites (2×2 arrangement)
- Standard for main characters
- Good detail/memory balance

*24×24 Actor:*
- Uses 9 hardware sprites (3×3)
- Memory intensive
- Reserved for bosses/special characters

*32×32 Actor:*
- Uses 16 hardware sprites (4×4)
- Extreme memory usage
- Rarely practical

**Sprite Sheet Organization:**

GBStudio requires specific sprite sheet layouts:

```
Static Sprite (16×16):
[Single 16×16 image]

Animated Actor (96×16):
[Idle][Walk1][Walk2][Walk3][Walk4][Walk5]
Six 16×16 frames in horizontal strip
```

**Animation Frame Limits:**
- Maximum 25 frames per animation
- Stored as 400×16 pixel strip maximum
- Must balance smoothness with memory

### Memory Management Strategy

**Tile Limits:**
- 64 unique sprite tiles (without background compromise)
- 96 unique sprite tiles (sacrificing background tiles)
- 192 background tiles (monochrome)
- 384 background tiles (Game Boy Color)

**Practical Implications:**

Each 16×16 sprite uses 4 tiles. Therefore:
- 64 tiles ÷ 4 = 16 unique sprite frames
- 96 tiles ÷ 4 = 24 unique sprite frames

This means your main character, enemies, and items share this limit!

**Memory Optimization Techniques:**

*Tile Reuse:*
Design sprites with repeated elements:
- Symmetrical designs (flip for different directions)
- Modular parts (swap heads, weapons)
- Shared body parts between characters

*Animation Efficiency:*
- Use fewer frames (3-4 can work)
- Animate only moving parts
- Share frames between animations

### Creating GBStudio-Compliant Assets

**Workspace Setup:**

1. Create new file: 16×16 pixels
2. Sprite > Color Mode > Indexed
3. Load GBStudio palette (save these exact colors)
4. Set background to Color 0 (transparent for sprites)

**Sprite Creation Workflow:**

**Step 1: Design with Constraints**
- Use only 3 colors for sprites
- Ensure readability at 1× zoom
- Test against different backgrounds

**Step 2: Animation Planning**
```
Frame 1: Idle
Frame 2-3: Walk cycle
Frame 4: Jump
Frame 5: Action
Frame 6: Damage
```

**Step 3: Export Preparation**
- Arrange frames horizontally
- No spacing between frames
- Export as PNG
- Indexed color mode preserved

### Background Tile Strategy

Backgrounds use different constraints than sprites:

**Tile Efficiency:**
Design backgrounds with reusable 8×8 tiles:
- Create base tiles (ground, walls)
- Design variants (damaged, decorated)
- Plan connections (corners, edges)

**Color Usage:**
Backgrounds can use all 4 colors effectively:
- Color 3: Outlines, deep shadows
- Color 2: Mid-tones, secondary shadows
- Color 1: Base colors, main surfaces
- Color 0: Highlights, sky, bright areas

**Scrolling Considerations:**
Game Boy scrolls in 8-pixel increments:
- Design tiles to work at any scroll position
- Avoid patterns that create scrolling artifacts
- Test with movement to ensure smooth visuals

### Practical Exercise: GBStudio Sprite Creation

**Project: Create a Complete Character Set**

**Character Design Requirements:**
- 16×16 pixel character
- 3 colors only (no Color 2)
- Readable silhouette
- Personality through pixels

**Animation Set:**
1. Idle (1 frame minimum, 2-3 for breathing)
2. Walk (4 frames for smooth motion)
3. Jump (1-2 frames)
4. Action (1 frame - sword swing, spell cast)

**Step-by-Step Process:**

1. **Create Base Sprite:**
   - New file: 16×16, indexed color
   - Draw character facing right
   - Use Color 3 for outlines
   - Color 1 for main body
   - Color 0 for highlights only

2. **Walking Animation:**
   - Frame 1: Contact pose (foot forward)
   - Frame 2: Passing pose (legs crossing)
   - Frame 3: Contact pose (opposite foot)
   - Frame 4: Passing pose (return)

3. **Export Format:**
   - Arrange all frames horizontally
   - No gaps between frames
   - Save as "character_walk.png"
   - Verify indexed color preserved

**Testing in GBStudio:**
1. Import sprite sheet
2. Set animation speed (15 fps typical)
3. Test in game scene
4. Adjust if readability issues

## Session 3.2: NES/NESmaker Technical Mastery

### The NES Architecture Deep Dive

The Nintendo Entertainment System's Picture Processing Unit (PPU) creates specific constraints that define the 8-bit aesthetic. Unlike modern systems, the NES generates graphics through clever hardware tricks.

**System Architecture:**
- Resolution: 256×240 pixels (256×224 visible NTSC)
- Pattern Tables: 2 tables, 256 tiles each
- Nametables: Screen layout data
- Attribute Tables: Color assignment
- Sprites: 64 sprites, 8 per scanline

### Understanding CHR ROM Organization

**Pattern Tables Explained:**

The NES stores graphics in two pattern tables:
- Table 0: Typically backgrounds ($0000-$0FFF)
- Table 1: Typically sprites ($1000-$1FFF)

Each table holds 256 8×8 pixel tiles, stored as 2-bit depth.

**Tile Format:**
Each 8×8 tile uses 16 bytes:
- 8 bytes for bit plane 0
- 8 bytes for bit plane 1
- Combined creates 2-bit (4 color) image

**Creating CHR-Compatible Graphics:**

1. **Work in 8×8 Grid:**
   - Create new file: 128×128 pixels
   - Enable grid: 8×8 pixels
   - Snap to grid enabled

2. **Design Within Tiles:**
   - Each 8×8 section is one tile
   - Plan connections between tiles
   - Number tiles mentally (0-255)

### The NES Palette System

**Total Palette Capability:**
- 64 colors available in hardware
- 25 colors displayable simultaneously
- Specific color limitations per area

**Background Palettes:**
```
4 palettes × 3 colors each = 12 colors
+ 1 universal background color = 13 total
```

Each 16×16 pixel area uses one palette.

**Sprite Palettes:**
```
4 palettes × 3 colors each = 12 colors
Color 0 always transparent
```

Each sprite selects one of four palettes.

**NES Color Values (Hex):**
Common colors used in NESmaker:
```
$0F - Black (universal background)
$00 - Gray
$10 - Light gray
$20 - White
$16 - Red
$1A - Green
$12 - Blue
$27 - Orange
$17 - Brown
```

**Palette Planning Strategy:**

*Environmental Palette Set:*
- Palette 0: Grass/Trees (greens, brown)
- Palette 1: Stone/Castle (grays, blue)
- Palette 2: Water/Sky (blues, white)
- Palette 3: Special/Effects (varies)

*Character Palette Set:*
- Palette 0: Player (skin, clothes, accent)
- Palette 1: Enemy type 1
- Palette 2: Enemy type 2
- Palette 3: Items/Effects

### Attribute Table Complexity

The attribute table assigns palettes to background tiles in 16×16 pixel blocks (2×2 tiles). This creates the "attribute clash" characteristic of NES games.

**Visualization:**
```
[Tile A][Tile B]  <- Same palette
[Tile C][Tile D]  <- Same palette
```

**Design Implications:**
- Plan 16×16 blocks to use same palette
- Place palette transitions at block boundaries
- Design tiles to work with multiple palettes

### Sprite Limitations and Flickering

**8 Sprites Per Scanline:**
The NES can only display 8 sprites on any horizontal line. The 9th+ sprites disappear, causing flickering.

**Mitigation Strategies:**
- Design enemies to stay at different heights
- Use sprite cycling (alternate which disappear)
- Plan boss fights with limitation in mind
- Keep projectiles on different scanlines

**Sprite Size Options:**
- 8×8: Standard, most flexible
- 8×16: Taller sprites, fewer objects

8×16 mode affects ALL sprites globally.

### NESmaker Workflow Integration

**Asset Preparation Pipeline:**

1. **Create Graphics in Aseprite:**
   - Use NES palette constraints
   - Design in 8×8 tile grid
   - Export as PNG

2. **Convert to CHR Format:**
   - NESmaker handles conversion
   - Verify tile usage (256 limit)
   - Check attribute table alignment

3. **Import and Test:**
   - Load into NESmaker
   - Assign palettes
   - Test in emulator

**Metatile Strategy:**

NESmaker uses "metatiles" - 16×16 blocks composed of 4 tiles:
```
[TL][TR]  TL = Top Left
[BL][BR]  TR = Top Right, etc.
```

Design metatiles for efficient level building:
- Ground blocks
- Platform variations
- Decorative elements

### Practical Exercise: NES Asset Creation

**Project: Create NES-Compatible Tileset**

**Requirements:**
- 32 unique 8×8 tiles
- 4 background palettes
- Seamless tiling
- Attribute-table friendly

**Step-by-Step Creation:**

1. **Setup Canvas:**
   - New file: 128×128 pixels
   - Grid: 8×8 pixels
   - Indexed color mode
   - Load NES palette

2. **Design Base Tiles:**
   - Tiles 0-7: Ground variations
   - Tiles 8-15: Platform edges
   - Tiles 16-23: Decorative elements
   - Tiles 24-31: Special/animated

3. **Create Metatiles:**
   - Combine 4 tiles into 16×16 blocks
   - Ensure palette consistency
   - Test different arrangements

4. **Palette Assignment:**
   - Group tiles by palette needs
   - Document which tiles use which palette
   - Create palette guide image

5. **Export for NESmaker:**
   - Save as indexed PNG
   - Maintain exact palette order
   - Include documentation

## Session 3.3: Godot Pixel Art Configuration

### Understanding Godot's Rendering Pipeline

Godot 4's rendering system offers powerful features that can help or hinder pixel art. Understanding these systems ensures pixel-perfect display across all devices.

**Key Concepts:**
- Viewport scaling
- Texture filtering
- Pixel snapping
- Camera movement
- Import settings

### Project Configuration for Pixel Art

**Project Settings Setup:**

Navigate to Project > Project Settings:

**Display/Window:**
```
Size:
- Viewport Width: 640
- Viewport Height: 360
- Window Width Override: 1280
- Window Height Override: 720
- Mode: Windowed
- Resizable: On
```

**Why These Numbers?**
640×360 is exactly 2× a common pixel art resolution (320×180) and scales perfectly to 720p and 1080p displays.

**Stretch Settings:**
```
Mode: canvas_items
Aspect: keep
Scale: 1.0
Scale Mode: integer
```

Integer scaling ensures no pixel distortion.

**Rendering Settings:**

**Textures:**
```
Canvas Textures:
- Default Texture Filter: Nearest
- Default Texture Repeat: Disabled
```

**Environment:**
```
Default Clear Color: Your background color
Use Pixel Snap: On (critical for movement)
```

**Anti-aliasing:**
```
MSAA 2D: Disabled
FXAA: Disabled
TAA: Disabled
```

All anti-aliasing must be disabled for crisp pixels.

### Import Settings Optimization

**Default Import Preset Creation:**

1. Select any PNG in FileSystem
2. Go to Import tab
3. Configure:
   - Filter: Off
   - Mipmaps: Off
   - Fix Alpha Border: Off
   - Premult Alpha: Off
   - sRGB: Off
   - Compress Mode: Lossless

4. Click "Preset" > "Save as Default"

Now all imported pixel art uses correct settings.

**Batch Processing Existing Assets:**
1. Select all sprites in FileSystem
2. Reimport with new settings
3. Verify in inspector

### Camera Configuration for Pixel-Perfect Movement

**Camera2D Setup:**

```gdscript
extends Camera2D

func _ready():
    # Enable pixel snap
    position_smoothing_enabled = false
    # Set zoom for pixel-perfect scaling
    zoom = Vector2(2, 2)  # Adjust based on your needs

func _process(_delta):
    # Snap camera to pixel grid
    global_position = global_position.round()
```

**Smooth Camera with Pixel Snap:**

```gdscript
extends Camera2D

var target_position: Vector2
var follow_speed: float = 5.0

func _process(delta):
    if target:
        target_position = target.global_position
        global_position = global_position.lerp(
            target_position.round(),
            follow_speed * delta
        )
        # Final snap to pixel
        global_position = global_position.round()
```

### Viewport Configuration for Multiple Resolutions

**Scalable Viewport Setup:**

Create a scene structure:
```
Main (Node2D)
└── SubViewportContainer (stretch mode: keep aspect)
    └── SubViewport (size: 320×180)
        └── Game Scene
```

**SubViewport Settings:**
- Size: Your base resolution
- Render Target Update: Always
- Canvas Item Default Filter: Nearest

This maintains pixel perfection at any window size.

### AnimationPlayer and Pixel Art

**Sprite Animation Setup:**

When animating position:
1. Use discrete values (no decimals)
2. Set animation interpolation to "Nearest"
3. Snap keyframes to integer positions

**Example Animation Track:**
```
Position track:
Frame 0: (0, 0)
Frame 10: (16, 0)  # Move exactly 16 pixels
Frame 20: (32, 0)  # Not 31.5 or 32.1
```

### Testing Across Different Scales

**Resolution Test Checklist:**

Test your game at:
- 1× scale (320×180 window)
- 2× scale (640×360 window)
- 3× scale (960×540 window)
- 4× scale (1280×720 window)
- Fullscreen on various monitors

Look for:
- Pixel distortion
- Uneven pixel sizes
- Blurry edges
- Shimmering during movement

### Practical Exercise: Godot Integration Test

**Project: Setup and Test Pixel Art Scene**

1. **Create Test Assets in Aseprite:**
   - 16×16 character sprite
   - 32×32 tileset (4 tiles)
   - 8×8 UI elements
   - All exported as PNG

2. **Setup Godot Project:**
   - Configure all project settings
   - Import assets with correct settings
   - Create test scene

3. **Build Test Scene:**
   - TileMap with your tiles
   - Character with 8-direction movement
   - UI overlay
   - Parallax background

4. **Movement Script:**
```gdscript
extends CharacterBody2D

const SPEED = 60.0  # Pixels per second

func _physics_process(delta):
    var direction = Input.get_vector(
        "ui_left", "ui_right",
        "ui_up", "ui_down"
    )

    if direction:
        velocity = direction * SPEED
        # Snap to pixel grid
        position = position.round()
    else:
        velocity = Vector2.ZERO

    move_and_slide()
```

5. **Test at Multiple Resolutions:**
   - Verify pixel perfection
   - Check movement smoothness
   - Ensure UI scales correctly
