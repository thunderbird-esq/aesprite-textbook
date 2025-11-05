#!/usr/bin/env python3
"""
prompt_generator.py - Generates XML prompts for nano-banana via Gemini
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
import hashlib

class PromptGenerator:
    """Generates hyper-specific XML prompts from layout configs"""
    
    def __init__(self):
        # Load master configuration
        with open('config/master_config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Component-specific prompt templates
        self.templates = {
            'graphic_photo_instructional': self.generate_photo_prompt,
            'container_featurebox': self.generate_container_prompt,
            'graphic_splat_container': self.generate_splat_prompt,
            'graphic_pixelart': self.generate_pixelart_prompt,
            'graphic_gui_recreation': self.generate_gui_prompt,
            'graphic_doodle': self.generate_doodle_prompt,
            'container_embossed_featurebox': self.generate_embossed_prompt
        }
        
        # Standard negative prompts by category
        self.negative_prompts = {
            'modern_tech': [
                'wireless mouse', 'optical mouse', 'gaming mouse', 'RGB lighting',
                'USB cable', 'wireless', 'bluetooth', 'LED', 'LCD screen',
                'flat screen', 'widescreen', 'smartphone', 'tablet'
            ],
            'modern_design': [
                'gradient', 'soft shadow', 'blur', 'transparency', 'glow',
                'bevel effect', '3D rendering', 'photorealistic', 'HDR',
                'depth of field', 'bokeh', 'lens flare', 'modern', 'minimal',
                'flat design', 'material design', 'anti-aliasing'
            ],
            'wrong_era': [
                'Windows 95', 'Windows', 'PC', 'IBM', 'modern computer',
                '2000s', '2010s', 'contemporary', 'current', 'new'
            ],
            'wrong_style': [
                'professional photography', 'stock photo', 'artistic',
                'dramatic lighting', 'moody', 'cinematic', 'stylized',
                'abstract', 'conceptual', 'fine art'
            ]
        }
    
    def generate_photo_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for instructional photography"""
        
        # Extract specifications
        subject = element.get('subject', 'hand using mouse')
        camera_settings = element.get('camera', {})
        lighting = element.get('lighting', {})
        
        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_photo_instructional</element_type>
    
    <image_specifications>
        <dimensions width="{element['dimensions'][0]}" height="{element['dimensions'][1]}" />
        <resolution dpi="300" />
        <color_mode>RGB</color_mode>
        <bit_depth>24</bit_depth>
    </image_specifications>
    
    <photographic_parameters>
        <film_stock>Kodak Gold 400</film_stock>
        <film_characteristics>
            <grain_index>39</grain_index>
            <grain_pattern>silver_halide_cubic</grain_pattern>
            <color_profile>
                <highlights>warm_bias</highlights>
                <midtones>neutral</midtones>
                <shadows>slight_cyan_shift</shadows>
            </color_profile>
        </film_characteristics>
        
        <camera_settings>
            <lens>{camera_settings.get('lens', '100mm macro')}</lens>
            <aperture>{camera_settings.get('aperture', 'f/11')}</aperture>
            <shutter_speed>{camera_settings.get('shutter', '1/125')}</shutter_speed>
            <focus_distance>{camera_settings.get('focus', '8 inches')}</focus_distance>
        </camera_settings>
        
        <lighting_setup>
            <ambient_level>moderate</ambient_level>
            <key_light>
                <type>softbox_24x36_inch</type>
                <position_horizontal>45_degrees_left</position_horizontal>
                <position_vertical>30_degrees_above</position_vertical>
                <distance>24_inches</distance>
                <power>100_percent</power>
                <color_temperature>5500K</color_temperature>
            </key_light>
            <fill_light>
                <type>white_foamcore_reflector</type>
                <position_horizontal>60_degrees_right</position_horizontal>
                <distance>18_inches</distance>
                <efficiency>50_percent</efficiency>
            </fill_light>
        </lighting_setup>
    </photographic_parameters>
    
    <subject_description>
        <primary>{subject}</primary>
        <details>
            <hand_age>8-10 years old</hand_age>
            <hand_characteristics>child-sized, natural, unprofessional</hand_characteristics>
            <mouse_model>Apple Desktop Bus Mouse M0100</mouse_model>
            <mouse_color>beige plastic with slight yellowing from age</mouse_color>
            <mouse_details>rectangular shape, single button, visible ADB cable</mouse_details>
            <background>solid color mousepad, royal blue fabric surface</background>
        </details>
    </subject_description>
    
    <composition>
        <angle>high angle, approximately 45 degrees from horizontal</angle>
        <framing>mouse fills 60% of frame, hand partially visible</framing>
        <focus_point>mouse button and index finger</focus_point>
        <depth_of_field>moderate, f/11 for sharp detail throughout</depth_of_field>
    </composition>
    
    <positive_prompt>
        Professional instructional photograph from 1996 children's computer book,
        8-year-old child's hand demonstrating proper grip on beige Apple M0100
        rectangular mouse, single button mouse with coiled ADB cable visible,
        index finger positioned correctly on mouse button, natural child grip,
        photographed on Kodak Gold 400 35mm film with visible grain structure,
        characteristic warm highlights and neutral midtones of Gold 400 film,
        high angle view showing mouse and partial hand, royal blue mousepad
        background, even lighting from softbox creating soft but defined shadows,
        sharp focus throughout with f/11 aperture, educational photography style,
        bright and approachable mood, slight film grain visible, authentic
        1990s color reproduction
    </positive_prompt>
    
    <negative_prompt>
        {', '.join(self.negative_prompts['modern_tech'])},
        {', '.join(self.negative_prompts['modern_design'])},
        {', '.join(self.negative_prompts['wrong_style'])},
        adult hands, professional hand model, manicured nails,
        jewelry, watches, dramatic shadows, artistic composition,
        shallow depth of field, two-button mouse, scroll wheel,
        dark mood, low key lighting, high contrast
    </negative_prompt>
</nano_banana_prompt>"""
        
        return xml_prompt
    
    def generate_container_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for feature box containers"""
        
        bg_color = element.get('background', '#FFD700')
        border = element.get('border', '4px solid black')
        
        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>container_featurebox</element_type>
    
    <geometry>
        <dimensions width="{element['dimensions'][0]}" height="{element['dimensions'][1]}" />
        <rotation degrees="{element.get('rotation', 0)}" />
    </geometry>
    
    <visual_properties>
        <background>
            <type>solid_color</type>
            <color>{bg_color}</color>
            <texture>none</texture>
        </background>
        
        <border>
            <style>solid</style>
            <width>4px</width>
            <color>#000000</color>
            <corners>square</corners>
        </border>
        
        <shadow>
            <type>hard_drop_shadow</type>
            <offset_x>3px</offset_x>
            <offset_y>3px</offset_y>
            <blur>0px</blur>
            <color>#000000</color>
            <opacity>100%</opacity>
        </shadow>
    </visual_properties>
    
    <positive_prompt>
        Flat rectangular container with solid {bg_color} background,
        thick 4 pixel black border with perfectly square corners,
        hard-edged drop shadow offset 3 pixels right and 3 pixels down,
        pure black shadow with no blur or softness, 1996 desktop
        publishing aesthetic, primitive digital graphic design,
        no gradients or modern effects
    </positive_prompt>
    
    <negative_prompt>
        gradient, soft shadow, blur, rounded corners, bevel,
        3D effect, transparency, anti-aliasing, modern design,
        subtle, sophisticated, professional, glossy, texture
    </negative_prompt>
</nano_banana_prompt>"""
        
        return xml_prompt
    
    def generate_splat_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for Nickelodeon-style splat containers"""
        
        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_splat_container</element_type>
    
    <geometry>
        <dimensions width="{element['dimensions'][0]}" height="{element['dimensions'][1]}" />
        <rotation degrees="{element.get('rotation', 0)}" />
    </geometry>
    
    <visual_properties>
        <splat_characteristics>
            <color>#F57D0D</color>  <!-- Nickelodeon Orange -->
            <style>organic_blob</style>
            <edges>irregular</edges>
            <splatter_points>3-5</splatter_points>
        </splat_characteristics>
    </visual_properties>
    
    <positive_prompt>
        Nickelodeon-style orange splat shape, Pantone Orange 021 C color
        (#F57D0D), organic blob with irregular edges and 3-5 splatter points,
        flat solid color with no gradients, hard edges, 1996 Nickelodeon
        branding aesthetic, energetic and playful shape, slightly asymmetric,
        like spilled paint or slime
    </positive_prompt>
    
    <negative_prompt>
        gradient, soft edges, blur, drop shadow, 3D effect,
        perfect circle, geometric shape, modern design, subtle,
        transparency, texture, shading, highlights
    </negative_prompt>
</nano_banana_prompt>"""
        
        return xml_prompt
    
    def generate_pixelart_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for pixel art sprites"""
        
        palette = element.get('palette', 'NES_limited')
        magnification = element.get('magnification', 8)
        
        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_pixelart</element_type>
    
    <pixel_specifications>
        <base_resolution>32x32</base_resolution>
        <display_magnification>{magnification}x</display_magnification>
        <interpolation>nearest_neighbor</interpolation>
        <antialiasing>none</antialiasing>
    </pixel_specifications>
    
    <color_palette>
        <type>{palette}</type>
        <colors>
            <color index="0">#000000</color>  <!-- Black -->
            <color index="1">#FFFFFF</color>  <!-- White -->
            <color index="2">#FF0000</color>  <!-- Red -->
            <color index="3">#00FF00</color>  <!-- Green -->
            <color index="4">#0000FF</color>  <!-- Blue -->
            <color index="5">#FFFF00</color>  <!-- Yellow -->
            <color index="6">#FF00FF</color>  <!-- Magenta -->
            <color index="7">#00FFFF</color>  <!-- Cyan -->
            <color index="8">#C0C0C0</color>  <!-- Light Gray -->
            <color index="9">#808080</color>  <!-- Dark Gray -->
            <color index="10">#800000</color> <!-- Dark Red -->
            <color index="11">#008000</color> <!-- Dark Green -->
            <color index="12">#000080</color> <!-- Dark Blue -->
            <color index="13">#808000</color> <!-- Olive -->
            <color index="14">#800080</color> <!-- Purple -->
            <color index="15">#008080</color> <!-- Teal -->
        </colors>
    </color_palette>
    
    <subject>{element.get('subject', 'pixel monster sprite')}</subject>
    
    <positive_prompt>
        8-bit pixel art sprite, 32x32 pixel base resolution scaled up {magnification}x
        with nearest neighbor interpolation, hard pixel edges with no anti-aliasing,
        limited {palette} color palette, retro video game aesthetic circa 1990,
        clear readable sprite design, solid colors per pixel, no blending
    </positive_prompt>
    
    <negative_prompt>
        anti-aliasing, smooth edges, gradient, blur, high resolution,
        modern pixel art, detailed shading, transparency, soft pixels,
        interpolation artifacts, photorealistic, 3D rendering
    </negative_prompt>
</nano_banana_prompt>"""
        
        return xml_prompt
    
    def generate_gui_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for GUI recreation (MacPaint/Aseprite)"""
        
        software = element.get('software', 'MacPaint')
        
        if software == 'MacPaint':
            xml_prompt = self.generate_macpaint_gui(element)
        else:
            xml_prompt = self.generate_aseprite_gui(element)
        
        return xml_prompt
    
    def generate_macpaint_gui(self, element: Dict[str, Any]) -> str:
        """Generate MacPaint interface recreation"""
        
        return f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_gui_recreation</element_type>
    
    <software_interface>
        <application>MacPaint 1.0</application>
        <os>Apple System 6</os>
        <year>1984-1990</year>
    </software_interface>
    
    <interface_elements>
        <window>
            <title_bar>
                <text>untitled</text>
                <font>Chicago 12pt</font>
                <close_box>left</close_box>
                <zoom_box>none</zoom_box>
            </title_bar>
            
            <menu_bar>
                <items>File Edit Goodies Font FontSize Style</items>
                <font>Chicago 12pt</font>
            </menu_bar>
            
            <tool_palette>
                <position>left</position>
                <tools>
                    <row1>line_thickness_options</row1>
                    <row2>selection_rectangle lasso</row2>
                    <row3>pencil paintbrush</row3>
                    <row4>paint_bucket spray_can</row4>
                    <row5>line rectangle</row5>
                    <row6>oval polygon</row6>
                </tools>
            </tool_palette>
            
            <pattern_palette>
                <position>bottom</position>
                <patterns>38 standard MacPaint patterns</patterns>
                <display>8x5 grid</display>
            </pattern_palette>
        </window>
        
        <canvas>
            <dimensions>576x720</dimensions>
            <color_mode>1-bit monochrome</color_mode>
            <dithering>Atkinson dithering</dithering>
        </canvas>
    </interface_elements>
    
    <visual_style>
        <colors>pure black and white only</colors>
        <fonts>Chicago bitmap font</fonts>
        <shadows>none</shadows>
        <effects>stippled patterns for gray simulation</effects>
    </visual_style>
    
    <positive_prompt>
        Perfect recreation of MacPaint 1.0 interface from Apple System 6,
        monochrome black and white only, Chicago bitmap font for all text,
        no anti-aliasing, tool palette on left with 6 rows of tools,
        pattern palette at bottom with 38 patterns in grid, single pixel
        black borders, stippled patterns to simulate grayscale,
        Atkinson dithering for images, authentic 1984-1990 Macintosh
        software interface
    </positive_prompt>
    
    <negative_prompt>
        color, grayscale, anti-aliasing, smooth fonts, gradients,
        shadows, modern UI, Windows, transparency, 3D effects,
        rounded corners, subtle design, contemporary interface
    </negative_prompt>
</nano_banana_prompt>"""
    
    def generate_aseprite_gui(self, element: Dict[str, Any]) -> str:
        """Generate simplified Aseprite interface for teaching"""
        
        return f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_gui_recreation</element_type>
    
    <software_interface>
        <application>Aseprite (simplified for kids)</application>
        <style>1996 software aesthetic</style>
    </software_interface>
    
    <interface_elements>
        <color_picker>
            <type>RGB sliders</type>
            <display>simplified grid</display>
            <preset_palette>16 colors</preset_palette>
        </color_picker>
        
        <tool_icons>
            <pencil>single pixel drawing</pencil>
            <eraser>pixel removal</eraser>
            <paint_bucket>flood fill</paint_bucket>
            <rectangle>shape tool</rectangle>
        </tool_icons>
        
        <canvas_grid>
            <visible>true</visible>
            <size>32x32 pixels</size>
            <grid_lines>1px gray</grid_lines>
        </canvas_grid>
    </interface_elements>
    
    <positive_prompt>
        Simplified pixel art software interface designed for children,
        basic tool palette with pencil eraser bucket and shapes,
        16 color palette grid, visible pixel grid on canvas,
        1996 software design aesthetic with gray 3D borders,
        simple and clear icons, educational software appearance
    </positive_prompt>
    
    <negative_prompt>
        modern UI, flat design, complex interface, professional software,
        dark theme, transparency, advanced tools, layers panel,
        timeline, animation controls
    </negative_prompt>
</nano_banana_prompt>"""
    
    def generate_doodle_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for hand-drawn doodles"""
        
        doodle_type = element.get('doodle_type', 'arrow')
        
        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>graphic_doodle</element_type>
    
    <doodle_specifications>
        <type>{doodle_type}</type>
        <style>hand_drawn</style>
        <line_weight>3-5px</line_weight>
        <color>#000000</color>
        <consistency>slightly_uneven</consistency>
    </doodle_specifications>
    
    <characteristics>
        <line_quality>confident but imperfect</line_quality>
        <corners>slightly rounded from marker tip</corners>
        <ends>natural taper or blob from lifting marker</ends>
    </characteristics>
    
    <positive_prompt>
        Hand-drawn {doodle_type} with thick black marker, confident
        single stroke, slightly uneven line weight, natural imperfections,
        looks like drawn by enthusiastic teacher on whiteboard,
        3-5 pixel thick line, no perfectly straight lines,
        organic and energetic appearance
    </positive_prompt>
    
    <negative_prompt>
        perfect geometry, vector graphics, thin line, pencil,
        tentative strokes, multiple strokes, shading, gradient,
        computer-generated, precise, mathematical, ruler-drawn
    </negative_prompt>
</nano_banana_prompt>"""
        
        return xml_prompt
    
    def generate_embossed_prompt(self, element: Dict[str, Any]) -> str:
        """Generate XML prompt for embossed feature boxes"""
        
        text = element.get('embossed_text', 'TIP!')
        
        xml_prompt = f"""
<nano_banana_prompt>
    <element_id>{element['id']}</element_id>
    <element_type>container_embossed_featurebox</element_type>
    
    <embossing_specifications>
        <technique>blind_embossing</technique>
        <depth>15-25 microns</depth>
        <style>raised_from_behind</style>
        <text>{text}</text>
        <font>Chicago or similar bold sans-serif</font>
    </embossing_specifications>
    
    <visual_effect>
        <highlights>top and left edges of raised areas</highlights>
        <shadows>bottom and right edges of raised areas</shadows>
        <surface>paper texture visible on raised portions</surface>
        <no_ink>true</no_ink>
        <no_foil>true</no_foil>
    </visual_effect>
    
    <positive_prompt>
        Blind embossed text "{text}" pressed into paper from behind,
        raised bumpy 3D letters with hard-edged highlights on top-left,
        hard shadows on bottom-right, no ink or color on letters,
        paper texture visible on raised surface, authentic embossing
        effect like Goosebumps book covers, tactile appearance
    </positive_prompt>
    
    <negative_prompt>
        printed text, ink, foil, color, flat, 2D, Photoshop bevel effect,
        soft inner glow, gradient, smooth, digital effect, letterpress,
        debossing, metallic, glossy
    </negative_prompt>
</nano_banana_prompt>"""
        
        return xml_prompt
    
    def create_gemini_metaprompt(self, element: Dict[str, Any]) -> str:
        """Create the prompt to send to Gemini for XML generation"""
        
        metaprompt = f"""
You are a specialized prompt engineer for a 1996 Klutz Press computer graphics workbook.
Generate a hyper-specific XML prompt for the nano-banana image model.

Element specifications:
- ID: {element['id']}
- Type: {element['type']}
- Dimensions: {element['dimensions']}
- Position: {element['position']}
- Additional specs: {json.dumps(element, indent=2)}

CRITICAL RULES:
1. Use ONLY quantitative language (pixels, degrees, hex colors)
2. NO subjective terms (nice, good, beautiful, modern)
3. Specify everything as if explaining to a machine
4. Include comprehensive negative prompts
5. Reference only 1996-available technology

The XML must follow this exact structure:
<nano_banana_prompt>
    <element_id>...</element_id>
    <element_type>...</element_type>
    [element-specific sections]
    <positive_prompt>...</positive_prompt>
    <negative_prompt>...</negative_prompt>
</nano_banana_prompt>

Generate the complete XML prompt now.
"""
        
        return metaprompt
    
    def generate_all_prompts(self, layout_file: str) -> Dict[str, str]:
        """Generate all prompts for a layout"""
        
        with open(layout_file, 'r') as f:
            layout = yaml.safe_load(f)
        
        prompts = {}
        
        for page in ['left_page', 'right_page']:
            for element in layout[page]['elements']:
                element_type = element['type']
                
                if element_type in self.templates:
                    # Generate specific prompt
                    xml_prompt = self.templates[element_type](element)
                    prompts[element['id']] = xml_prompt
                    
                    # Save to file
                    output_path = Path('prompts/components') / f"{element['id']}.xml"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(xml_prompt)
        
        return prompts


# Usage example
if __name__ == "__main__":
    generator = PromptGenerator()
    
    # Test element
    test_element = {
        'id': 'L_photo_mouse_01',
        'type': 'graphic_photo_instructional',
        'dimensions': [600, 450],
        'position': [250, 300],
        'subject': 'child hand using Apple mouse',
        'camera': {'lens': '100mm macro', 'aperture': 'f/11'}
    }
    
    # Generate prompt
    xml_prompt = generator.generate_photo_prompt(test_element)
    print(xml_prompt)
    
    # Generate all prompts for a layout
    prompts = generator.generate_all_prompts('config/layouts/spread_04_05.yaml')
    print(f"Generated {len(prompts)} prompts")
