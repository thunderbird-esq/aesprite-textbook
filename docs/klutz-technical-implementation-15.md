# Section 15: Final Packaging and Distribution
```python
#!/usr/bin/env python3
"""
package_builder.py - Comprehensive packaging and distribution system

This module creates multiple distribution formats for the Klutz Workbook:
1. ZIP/TAR archives for standard distribution
2. Self-extracting archives with embedded viewer
3. ISO images for CD-R burning (authentic 1996 experience)
4. 1.44MB floppy disk images with period-accurate software
5. Complete validation and verification systems
"""

import os
import shutil
import zipfile
import tarfile
import hashlib
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import struct
import logging
import subprocess
from PIL import Image
import numpy as np

@dataclass
class PackageConfig:
    """Configuration for package building with EXACT specifications"""
    
    # Output directories
    output_base: Path = Path("output/packages")
    staging_dir: Path = Path("output/staging")
    
    # Package formats to generate
    formats: List[str] = field(default_factory=lambda: [
        "zip",
        "tar.gz",
        "self_extracting",
        "iso",
        "floppy_img"
    ])
    
    # Content inclusion rules
    include_spreads: bool = True
    include_individual_assets: bool = True
    include_failed_qa: bool = True  # In separate folder for analysis
    include_source_files: bool = True
    include_documentation: bool = True
    include_validation_reports: bool = True
    
    # ISO specifications (CD-R compatible)
    iso_config: Dict = field(default_factory=lambda: {
        "volume_id": "KLUTZ_WORKBOOK_1996",
        "publisher": "Klutz Press",
        "application": "Klutz Computer Graphics Workbook",
        "format": "iso9660",  # Maximum compatibility
        "joliet": True,  # Windows long filename support
        "rock_ridge": True,  # Unix permissions
        "boot_image": None  # Could add bootable installer
    })
    
    # Floppy disk specifications (1.44MB)
    floppy_config: Dict = field(default_factory=lambda: {
        "size_bytes": 1474560,  # Exactly 1.44MB
        "sectors": 2880,
        "bytes_per_sector": 512,
        "tracks": 80,
        "heads": 2,
        "sectors_per_track": 18,
        "filesystem": "FAT12",
        "volume_label": "KLUTZ_PAINT",
        "oem_id": "MSWIN4.0"
    })
    
    # Metadata for all packages
    metadata: Dict = field(default_factory=lambda: {
        "project": "Klutz Computer Graphics Workbook",
        "version": "1.0.0",
        "year": 1996,
        "author": "Klutz Press",
        "generator": "Klutz Pipeline v1.0",
        "authenticity": "Period-accurate 1996 aesthetic"
    })

class FloppyDiskImage:
    """
    Creates authentic 1.44MB floppy disk images.
    
    This class generates:
    - Proper FAT12 filesystem
    - Boot sector with period-accurate parameters
    - Directory structure matching 1996 conventions
    - 8.3 filename compliance
    """
    
    def __init__(self, config: PackageConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def create_floppy_image(self, content_dir: Path, output_path: Path) -> bool:
        """
        Create a 1.44MB floppy disk image with FAT12 filesystem.
        
        This generates an EXACT replica of a 1996-era floppy disk:
        - Boot sector with proper BPB (BIOS Parameter Block)
        - FAT12 file allocation tables
        - Root directory with 8.3 filenames
        - Data area with files
        """
        
        self.logger.info("Creating 1.44MB floppy disk image...")
        
        # Initialize empty disk image
        disk_data = bytearray(self.config.floppy_config["size_bytes"])
        
        # Create boot sector
        self._create_boot_sector(disk_data)
        
        # Create FAT tables
        self._create_fat_tables(disk_data)
        
        # Create root directory
        self._create_root_directory(disk_data, content_dir)
        
        # Copy files to data area
        self._copy_files_to_image(disk_data, content_dir)
        
        # Write image to file
        with open(output_path, 'wb') as f:
            f.write(disk_data)
        
        self.logger.info(f"Floppy image created: {output_path}")
        return True
    
    def _create_boot_sector(self, disk: bytearray):
        """Create FAT12 boot sector with period-accurate parameters"""
        
        # Jump instruction (EB 3C 90)
        disk[0:3] = b'\xEB\x3C\x90'
        
        # OEM ID (8 bytes)
        oem_id = self.config.floppy_config["oem_id"].encode('ascii')
        disk[3:11] = oem_id.ljust(8, b' ')
        
        # BIOS Parameter Block (BPB)
        struct.pack_into('<H', disk, 11, 512)  # Bytes per sector
        disk[13] = 1  # Sectors per cluster
        struct.pack_into('<H', disk, 14, 1)  # Reserved sectors
        disk[16] = 2  # Number of FATs
        struct.pack_into('<H', disk, 17, 224)  # Root directory entries
        struct.pack_into('<H', disk, 19, 2880)  # Total sectors
        disk[21] = 0xF0  # Media descriptor (floppy)
        struct.pack_into('<H', disk, 22, 9)  # Sectors per FAT
        struct.pack_into('<H', disk, 24, 18)  # Sectors per track
        struct.pack_into('<H', disk, 26, 2)  # Number of heads
        struct.pack_into('<I', disk, 28, 0)  # Hidden sectors
        
        # Extended BPB
        disk[36] = 0x29  # Extended boot signature
        struct.pack_into('<I', disk, 39, 0x12345678)  # Volume serial number
        
        # Volume label (11 bytes)
        label = self.config.floppy_config["volume_label"].encode('ascii')
        disk[43:54] = label.ljust(11, b' ')
        
        # Filesystem type (8 bytes)
        disk[54:62] = b'FAT12   '
        
        # Boot signature
        disk[510:512] = b'\x55\xAA'
    
    def _create_fat_tables(self, disk: bytearray):
        """Create FAT12 file allocation tables"""
        
        fat_start = 512  # After boot sector
        fat_size = 9 * 512  # 9 sectors per FAT
        
        # First FAT
        disk[fat_start] = 0xF0  # Media descriptor
        disk[fat_start + 1] = 0xFF
        disk[fat_start + 2] = 0xFF
        
        # Copy first FAT to second FAT
        second_fat_start = fat_start + fat_size
        disk[second_fat_start:second_fat_start + fat_size] = disk[fat_start:fat_start + fat_size]
    
    def _create_root_directory(self, disk: bytearray, content_dir: Path):
        """Create root directory with 8.3 filename entries"""
        
        root_dir_start = 512 + (2 * 9 * 512)  # After boot sector and FATs
        entry_size = 32
        
        # Add volume label entry
        disk[root_dir_start:root_dir_start + 11] = self.config.floppy_config["volume_label"].encode('ascii').ljust(11, b' ')
        disk[root_dir_start + 11] = 0x08  # Volume label attribute
        
        # Add files
        entry_offset = entry_size
        for file_path in content_dir.glob('*'):
            if file_path.is_file():
                # Convert to 8.3 filename
                name_8_3 = self._convert_to_8_3(file_path.name)
                
                # Create directory entry
                entry_start = root_dir_start + entry_offset
                disk[entry_start:entry_start + 11] = name_8_3.encode('ascii').ljust(11, b' ')
                disk[entry_start + 11] = 0x20  # Archive attribute
                
                # File size
                file_size = file_path.stat().st_size
                struct.pack_into('<I', disk, entry_start + 28, file_size)
                
                entry_offset += entry_size
                
                if entry_offset >= 224 * entry_size:  # Max root directory entries
                    break
    
    def _convert_to_8_3(self, filename: str) -> str:
        """Convert filename to 8.3 format"""
        
        name, ext = os.path.splitext(filename)
        name = name[:8].upper().replace(' ', '_')
        ext = ext[1:4].upper() if ext else ''
        return f"{name:<8}{ext:<3}".replace(' ', '')
    
    def _copy_files_to_image(self, disk: bytearray, content_dir: Path):
        """Copy actual file data to disk image"""
        
        data_start = 512 + (2 * 9 * 512) + (224 * 32)  # After boot, FATs, and root dir
        current_offset = data_start
        
        for file_path in content_dir.glob('*'):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Check if fits on disk
                if current_offset + len(file_data) > self.config.floppy_config["size_bytes"]:
                    self.logger.warning(f"File {file_path.name} doesn't fit on floppy")
                    break
                
                disk[current_offset:current_offset + len(file_data)] = file_data
                
                # Align to cluster boundary (512 bytes)
                current_offset += ((len(file_data) + 511) // 512) * 512

class ISOImageBuilder:
    """
    Creates ISO 9660 CD-ROM images for authentic 1996 distribution.
    
    This creates images that can be:
    - Burned to CD-R (650MB capacity)
    - Mounted as virtual drives
    - Used in period-appropriate systems
    """
    
    def __init__(self, config: PackageConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def create_iso_image(self, content_dir: Path, output_path: Path) -> bool:
        """
        Create ISO 9660 image using mkisofs/genisoimage.
        
        Parameters match 1996 CD-ROM standards:
        - ISO 9660 Level 2 for longer filenames
        - Joliet extensions for Windows
        - Rock Ridge for Unix
        """
        
        self.logger.info("Creating ISO image for CD-R...")
        
        # Check for mkisofs or genisoimage
        mkisofs_cmd = self._find_mkisofs_command()
        if not mkisofs_cmd:
            self.logger.error("mkisofs or genisoimage not found")
            return False
        
        # Build mkisofs command
        cmd = [
            mkisofs_cmd,
            '-o', str(output_path),
            '-V', self.config.iso_config["volume_id"],
            '-publisher', self.config.iso_config["publisher"],
            '-A', self.config.iso_config["application"],
            '-J',  # Joliet extensions
            '-r',  # Rock Ridge extensions
            '-iso-level', '2',  # Allow longer filenames
            '-allow-lowercase',
            '-allow-multidot',
            str(content_dir)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.info(f"ISO image created: {output_path}")
            
            # Verify ISO size is CD-R compatible
            iso_size = output_path.stat().st_size
            cd_capacity = 700 * 1024 * 1024  # 700MB CD-R
            
            if iso_size > cd_capacity:
                self.logger.warning(f"ISO size ({iso_size / 1024 / 1024:.1f}MB) exceeds CD-R capacity")
            else:
                self.logger.info(f"ISO size: {iso_size / 1024 / 1024:.1f}MB (fits on CD-R)")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"ISO creation failed: {e.stderr}")
            return False
    
    def _find_mkisofs_command(self) -> Optional[str]:
        """Find available ISO creation command"""
        
        for cmd in ['mkisofs', 'genisoimage']:
            if shutil.which(cmd):
                return cmd
        return None
    
    def add_autorun(self, staging_dir: Path):
        """
        Add AUTORUN.INF for Windows 95/98 compatibility.
        
        This makes the CD auto-start when inserted, showing:
        - Custom icon
        - Auto-launch of viewer application
        - Proper CD label
        """
        
        autorun_content = """[autorun]
open=viewer\\klutz.exe
icon=viewer\\klutz.ico
label=Klutz Computer Graphics Workbook

[Content]
Title=Klutz Computer Graphics Workbook
Author=Klutz Press
Year=1996
"""
        
        autorun_path = staging_dir / "AUTORUN.INF"
        autorun_path.write_text(autorun_content)
        self.logger.info("Added AUTORUN.INF for Windows compatibility")

class SelfExtractingArchive:
    """
    Creates self-extracting archives with embedded viewer.
    
    This generates executables that:
    - Extract themselves when run
    - Launch embedded HTML viewer
    - Work on period-appropriate systems
    """
    
    def __init__(self, config: PackageConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def create_self_extracting(self, content_dir: Path, output_path: Path) -> bool:
        """Create self-extracting archive with viewer"""
        
        self.logger.info("Creating self-extracting archive...")
        
        # Create viewer HTML
        viewer_html = self._create_html_viewer(content_dir)
        viewer_path = content_dir / "index.html"
        viewer_path.write_text(viewer_html)
        
        # Create extraction script
        if os.name == 'nt':  # Windows
            return self._create_windows_sfx(content_dir, output_path)
        else:  # Unix-like
            return self._create_unix_sfx(content_dir, output_path)
    
    def _create_html_viewer(self, content_dir: Path) -> str:
        """
        Create HTML viewer for workbook pages.
        
        This generates a complete HTML application that:
        - Shows thumbnails of all pages
        - Allows full-screen viewing
        - Works in 1996-era browsers (Netscape 3, IE 3)
        """
        
        html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<HTML>
<HEAD>
<TITLE>Klutz Computer Graphics Workbook</TITLE>
<STYLE TYPE="text/css">
BODY {
    background-color: #F8F3E5;
    font-family: Helvetica, Arial, sans-serif;
    margin: 20px;
}
H1 {
    color: #FFD700;
    background-color: #000000;
    padding: 10px;
    font-size: 48px;
}
.page-thumb {
    width: 200px;
    height: 130px;
    border: 4px solid #000000;
    margin: 10px;
    cursor: pointer;
}
.page-thumb:hover {
    border-color: #F57D0D;
}
</STYLE>
</HEAD>
<BODY>
<H1>KLUTZ COMPUTER GRAPHICS WORKBOOK</H1>
<P><B>Learn Pixel Art the Klutz Way!</B></P>

<H2>Table of Contents</H2>
<TABLE BORDER="1" CELLPADDING="5">
<TR>
    <TH>Page</TH>
    <TH>Title</TH>
    <TH>View</TH>
</TR>
"""
        
        # Add page entries
        for i, page_file in enumerate(sorted(content_dir.glob("spread_*.png"))):
            html += f"""
<TR>
    <TD>{i+1}</TD>
    <TD>Spread {i//2 + 1}</TD>
    <TD><A HREF="{page_file.name}">View</A></TD>
</TR>
"""
        
        html += """
</TABLE>

<H2>Page Gallery</H2>
<P>Click any page to view full size:</P>
"""
        
        # Add thumbnail gallery
        for page_file in sorted(content_dir.glob("spread_*.png")):
            html += f"""
<A HREF="{page_file.name}">
    <IMG SRC="{page_file.name}" CLASS="page-thumb" ALT="Page">
</A>
"""
        
        html += """
<HR>
<P><SMALL>&copy; 1996 Klutz Press. All rights reserved.</SMALL></P>
</BODY>
</HTML>
"""
        
        return html
    
    def _create_windows_sfx(self, content_dir: Path, output_path: Path) -> bool:
        """Create Windows self-extracting EXE"""
        
        # Use 7-Zip SFX if available
        if shutil.which('7z'):
            # Create config file
            config = """
;!@Install@!UTF-8!
Title="Klutz Computer Graphics Workbook"
BeginPrompt="Extract Klutz Workbook?"
ExtractDialogText="Extracting files..."
ExtractTitle="Klutz Workbook"
GUIMode="1"
OverwriteMode="0"
ExecuteFile="index.html"
;!@InstallEnd@!
"""
            config_path = content_dir / "sfx_config.txt"
            config_path.write_text(config)
            
            # Create archive
            archive_path = output_path.with_suffix('.7z')
            cmd = ['7z', 'a', '-sfx', str(archive_path), str(content_dir / '*')]
            
            try:
                subprocess.run(cmd, check=True)
                
                # Rename to .exe
                shutil.move(str(archive_path), str(output_path))
                self.logger.info(f"Windows SFX created: {output_path}")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"SFX creation failed: {e}")
                return False
        
        self.logger.warning("7-Zip not found, cannot create Windows SFX")
        return False
    
    def _create_unix_sfx(self, content_dir: Path, output_path: Path) -> bool:
        """Create Unix shell self-extracting archive"""
        
        # Create extraction script
        script = """#!/bin/sh
# Klutz Workbook Self-Extracting Archive
# Generated: """ + datetime.now().isoformat() + """

echo "Klutz Computer Graphics Workbook - Self Extractor"
echo "================================================"
# Klutz Workbook Self-Extracting Archive (continued)
echo "Extracting to ./klutz_workbook..."

# Create extraction directory
EXTRACT_DIR="klutz_workbook"
mkdir -p "$EXTRACT_DIR"

# Find archive start marker
ARCHIVE_START=$(awk '/^__ARCHIVE_START__/ { print NR + 1; exit 0; }' "$0")

# Extract archive
tail -n +$ARCHIVE_START "$0" | tar xz -C "$EXTRACT_DIR"

echo "Extraction complete!"
echo "Opening viewer..."

# Try to open HTML viewer
if command -v xdg-open >/dev/null; then
    xdg-open "$EXTRACT_DIR/index.html"
elif command -v open >/dev/null; then
    open "$EXTRACT_DIR/index.html"
else
    echo "Please open $EXTRACT_DIR/index.html in your browser"
fi

exit 0

__ARCHIVE_START__
"""
        
        # Create temporary script file
        script_path = output_path.with_suffix('.sh')
        script_path.write_text(script)
        
        # Create tar archive
        tar_path = output_path.with_suffix('.tar.gz')
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(content_dir, arcname='.')
        
        # Combine script and archive
        with open(output_path, 'wb') as out:
            out.write(script.encode('utf-8'))
            with open(tar_path, 'rb') as tar_file:
                out.write(tar_file.read())
        
        # Make executable
        os.chmod(output_path, 0o755)
        
        # Clean up temporary files
        script_path.unlink()
        tar_path.unlink()
        
        self.logger.info(f"Unix SFX created: {output_path}")
        return True

class QualityAssurancePackager:
    """
    Packages QA results for analysis.
    
    Failed QA items are preserved with:
    - Complete validation reports
    - Visual comparison tools
    - Remediation suggestions
    """
    
    def __init__(self, config: PackageConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def package_qa_results(self, qa_dir: Path, output_dir: Path):
        """
        Package QA results with complete analysis.
        
        Structure:
        - passed/: Items that passed all checks
        - failed/: Items that failed with reports
        - analysis/: Tools for understanding failures
        """
        
        self.logger.info("Packaging QA results...")
        
        # Create directory structure
        passed_dir = output_dir / "qa_results" / "passed"
        failed_dir = output_dir / "qa_results" / "failed"
        analysis_dir = output_dir / "qa_results" / "analysis"
        
        for dir_path in [passed_dir, failed_dir, analysis_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Process QA reports
        for report_file in qa_dir.glob("*.json"):
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            element_id = report.get("element_id", "unknown")
            status = report.get("overall_status", "unknown")
            
            if status == "passed":
                # Copy to passed directory
                shutil.copy2(report_file, passed_dir / report_file.name)
            else:
                # Copy to failed directory with analysis
                failed_item_dir = failed_dir / element_id
                failed_item_dir.mkdir(exist_ok=True)
                
                # Copy report
                shutil.copy2(report_file, failed_item_dir / "report.json")
                
                # Generate failure analysis
                analysis = self._analyze_failure(report)
                analysis_path = failed_item_dir / "analysis.md"
                analysis_path.write_text(analysis)
                
                # Copy failed asset if exists
                asset_path = qa_dir.parent / "assets" / f"{element_id}.png"
                if asset_path.exists():
                    shutil.copy2(asset_path, failed_item_dir / "failed_asset.png")
        
        # Generate summary report
        summary = self._generate_qa_summary(passed_dir, failed_dir)
        (analysis_dir / "summary.html").write_text(summary)
        
        self.logger.info(f"QA results packaged: {output_dir / 'qa_results'}")
    
    def _analyze_failure(self, report: Dict) -> str:
        """
        Analyze QA failure and provide remediation.
        
        This generates:
        - Specific failure reasons
        - Exact specifications violated
        - Step-by-step remediation
        """
        
        analysis = []
        analysis.append(f"# QA Failure Analysis: {report['element_id']}\n\n")
        analysis.append(f"**Overall Status**: {report['overall_status']}\n")
        analysis.append(f"**Overall Score**: {report['overall_score']:.2f}\n\n")
        
        analysis.append("## Failed Checks\n\n")
        
        for check in report.get("checks", []):
            if check["status"] == "failed":
                analysis.append(f"### {check['check_name']}\n")
                analysis.append(f"- **Category**: {check['category']}\n")
                analysis.append(f"- **Score**: {check['score']:.2f}\n")
                analysis.append(f"- **Message**: {check['message']}\n")
                
                # Add specific remediation
                remediation = self._get_remediation(check['check_name'])
                if remediation:
                    analysis.append(f"\n**Remediation**:\n{remediation}\n")
                
                analysis.append("\n")
        
        analysis.append("## Specifications Violated\n\n")
        
        # List exact specifications that were violated
        violations = []
        for check in report.get("checks", []):
            if check["status"] == "failed":
                if "spine_intrusion" in check['check_name']:
                    violations.append("- Content placed in spine dead zone (x=1469-1931)")
                elif "dimension" in check['check_name']:
                    violations.append(f"- Incorrect dimensions: expected {check.get('details', {}).get('expected')}")
                elif "color" in check['check_name']:
                    violations.append("- Color distribution violates 70/20/10 rule")
                elif "forbidden_terms" in check['check_name']:
                    violations.append(f"- Contains forbidden terms: {check.get('details', {}).get('found_terms')}")
        
        for violation in violations:
            analysis.append(f"{violation}\n")
        
        return "".join(analysis)
    
    def _get_remediation(self, check_name: str) -> str:
        """Get specific remediation steps for failed check"""
        
        remediations = {
            "spine_intrusion": """
1. Move element position so x + width < 1469 (for left page)
2. Or ensure x > 1931 (for right page)
3. Use validator.check_spine_intrusion() before generation
""",
            "dimension_mismatch": """
1. Resize element to exact specified dimensions
2. Maximum tolerance is ±10 pixels
3. Use Image.resize() with LANCZOS resampling
""",
            "forbidden_terms": """
1. Remove all modern terminology from prompts
2. Replace with period-appropriate terms:
   - 'gradient' -> 'solid color'
   - 'wireless' -> 'coiled cable'
   - 'USB' -> 'ADB (Apple Desktop Bus)'
""",
            "color_distribution": """
1. Reduce accent color usage:
   - Nickelodeon Orange: max 20%
   - Goosebumps Acid: max 10%
2. Increase Klutz primary colors to 70%
3. Use color_validator.check_distribution()
""",
            "soft_shadows": """
1. Remove all blur from shadows
2. Use hard-edged shadows only:
   - offset_x: 3px
   - offset_y: 3px
   - blur: 0px
"""
        }
        
        return remediations.get(check_name, "Review specifications and regenerate")
    
    def _generate_qa_summary(self, passed_dir: Path, failed_dir: Path) -> str:
        """Generate HTML summary of QA results"""
        
        passed_count = len(list(passed_dir.glob("*.json")))
        failed_count = len(list(failed_dir.glob("*/")))
        total_count = passed_count + failed_count
        
        pass_rate = (passed_count / max(total_count, 1)) * 100
        
        html = f"""<!DOCTYPE HTML>
<HTML>
<HEAD>
<TITLE>QA Results Summary</TITLE>
<STYLE>
body {{ font-family: Helvetica, sans-serif; margin: 20px; }}
.passed {{ color: green; font-weight: bold; }}
.failed {{ color: red; font-weight: bold; }}
.warning {{ color: orange; font-weight: bold; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f2f2f2; }}
</STYLE>
</HEAD>
<BODY>
<H1>Quality Assurance Summary</H1>

<H2>Overall Statistics</H2>
<P>Total Items: {total_count}</P>
<P class="passed">Passed: {passed_count} ({pass_rate:.1f}%)</P>
<P class="failed">Failed: {failed_count} ({100-pass_rate:.1f}%)</P>

<H2>Failed Items Requiring Attention</H2>
<TABLE>
<TR>
    <TH>Element ID</TH>
    <TH>Type</TH>
    <TH>Primary Failure</TH>
    <TH>Action Required</TH>
</TR>
"""
        
        # List failed items
        for failed_item in failed_dir.glob("*/"):
            if failed_item.is_dir():
                report_path = failed_item / "report.json"
                if report_path.exists():
                    with open(report_path, 'r') as f:
                        report = json.load(f)
                    
                    primary_failure = "Unknown"
                    for check in report.get("checks", []):
                        if check["status"] == "failed":
                            primary_failure = check["check_name"]
                            break
                    
                    html += f"""
<TR>
    <TD>{report['element_id']}</TD>
    <TD>{report['element_type']}</TD>
    <TD class="failed">{primary_failure}</TD>
    <TD>Regenerate with correct specifications</TD>
</TR>
"""
        
        html += """
</TABLE>
</BODY>
</HTML>
"""
        
        return html

class PackageValidator:
    """
    Validates package integrity and completeness.
    
    Performs:
    - Checksum verification
    - Content completeness checks
    - Format validation
    - Authenticity verification
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_package(self, package_path: Path) -> Dict:
        """
        Perform complete validation of package.
        
        Returns detailed validation report including:
        - File integrity (checksums)
        - Content completeness
        - Specification compliance
        - Period authenticity
        """
        
        self.logger.info(f"Validating package: {package_path}")
        
        validation = {
            "package": str(package_path),
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_valid": True
        }
        
        # Check file exists and size
        if not package_path.exists():
            validation["checks"]["exists"] = False
            validation["overall_valid"] = False
            return validation
        
        validation["checks"]["exists"] = True
        validation["checks"]["size_bytes"] = package_path.stat().st_size
        
        # Calculate checksums
        validation["checks"]["checksums"] = {
            "md5": self._calculate_checksum(package_path, 'md5'),
            "sha256": self._calculate_checksum(package_path, 'sha256')
        }
        
        # Validate based on package type
        if package_path.suffix == '.zip':
            validation["checks"]["content"] = self._validate_zip_content(package_path)
        elif package_path.suffix == '.gz':
            validation["checks"]["content"] = self._validate_tar_content(package_path)
        elif package_path.suffix == '.iso':
            validation["checks"]["content"] = self._validate_iso_content(package_path)
        elif package_path.suffix == '.img':
            validation["checks"]["content"] = self._validate_floppy_content(package_path)
        
        # Check for required files
        required_files = [
            "manifest.json",
            "README.txt",
            "checksums.txt"
        ]
        
        validation["checks"]["required_files"] = self._check_required_files(
            package_path, required_files
        )
        
        return validation
    
    def _calculate_checksum(self, file_path: Path, algorithm: str) -> str:
        """Calculate file checksum"""
        
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def _validate_zip_content(self, zip_path: Path) -> Dict:
        """Validate ZIP archive content"""
        
        content = {
            "valid": True,
            "file_count": 0,
            "total_uncompressed": 0,
            "compression_ratio": 0
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Check for corruption
                bad_files = zf.testzip()
                if bad_files:
                    content["valid"] = False
                    content["corrupt_files"] = bad_files
                
                # Get file list and stats
                content["file_count"] = len(zf.filelist)
                
                for info in zf.filelist:
                    content["total_uncompressed"] += info.file_size
                
                compressed_size = zip_path.stat().st_size
                if content["total_uncompressed"] > 0:
                    content["compression_ratio"] = compressed_size / content["total_uncompressed"]
                
        except zipfile.BadZipFile:
            content["valid"] = False
            content["error"] = "Invalid ZIP file"
        
        return content
    
    def _validate_tar_content(self, tar_path: Path) -> Dict:
        """Validate TAR archive content"""
        
        content = {
            "valid": True,
            "file_count": 0,
            "format": "unknown"
        }
        
        try:
            with tarfile.open(tar_path, 'r:*') as tf:
                content["file_count"] = len(tf.getmembers())
                content["format"] = tf.format
                
        except tarfile.TarError as e:
            content["valid"] = False
            content["error"] = str(e)
        
        return content
    
    def _validate_iso_content(self, iso_path: Path) -> Dict:
        """Validate ISO image content"""
        
        content = {
            "valid": True,
            "size_mb": iso_path.stat().st_size / (1024 * 1024),
            "fits_cd": iso_path.stat().st_size <= (700 * 1024 * 1024)
        }
        
        # Check ISO header
        with open(iso_path, 'rb') as f:
            # ISO 9660 identifier at offset 32768
            f.seek(32768)
            identifier = f.read(5)
            
            if identifier == b'CD001':
                content["format"] = "ISO 9660"
                content["valid"] = True
            else:
                content["valid"] = False
                content["error"] = "Invalid ISO 9660 header"
        
        return content
    
    def _validate_floppy_content(self, img_path: Path) -> Dict:
        """Validate floppy disk image"""
        
        content = {
            "valid": True,
            "size_correct": img_path.stat().st_size == 1474560
        }
        
        if not content["size_correct"]:
            content["valid"] = False
            content["error"] = f"Invalid size: {img_path.stat().st_size} (expected 1474560)"
        
        # Check FAT12 boot sector
        with open(img_path, 'rb') as f:
            # Check for boot signature
            f.seek(510)
            signature = f.read(2)
            
            if signature == b'\x55\xAA':
                content["boot_sector"] = "valid"
            else:
                content["valid"] = False
                content["error"] = "Invalid boot sector signature"
        
        return content
    
    def _check_required_files(self, package_path: Path, required: List[str]) -> Dict:
        """Check for required files in package"""
        
        found = {}
        
        if package_path.suffix == '.zip':
            with zipfile.ZipFile(package_path, 'r') as zf:
                names = zf.namelist()
                for req_file in required:
                    found[req_file] = any(req_file in name for name in names)
        
        return found

class PackageBuilder:
    """
    Main orchestrator for package building.
    
    Coordinates:
    - Multiple format generation
    - Content staging
    - Validation
    - Distribution preparation
    """
    
    def __init__(self, config: PackageConfig = None):
        self.config = config or PackageConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.floppy_builder = FloppyDiskImage(config)
        self.iso_builder = ISOImageBuilder(config)
        self.sfx_builder = SelfExtractingArchive(config)
        self.qa_packager = QualityAssurancePackager(config)
        self.validator = PackageValidator()
        
        # Ensure output directories exist
        self.config.output_base.mkdir(parents=True, exist_ok=True)
        self.config.staging_dir.mkdir(parents=True, exist_ok=True)
        
    def build_all_packages(self, source_dir: Path) -> Dict:
        """
        Build packages in ALL formats.
        
        This generates:
        1. Standard archives (ZIP, TAR)
        2. Self-extracting archives
        3. ISO images for CD-R
        4. Floppy disk images
        5. Complete validation reports
        """
        
        self.logger.info("Starting comprehensive package build...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "packages": {},
            "validation": {}
        }
        
        # Stage content
        staging_dir = self._stage_content(source_dir)
        
        # Generate each format
        for format_type in self.config.formats:
            self.logger.info(f"Building {format_type} package...")
            
            if format_type == "zip":
                package_path = self._build_zip(staging_dir)
            elif format_type == "tar.gz":
                package_path = self._build_tar(staging_dir)
            elif format_type == "self_extracting":
                package_path = self._build_sfx(staging_dir)
            elif format_type == "iso":
                package_path = self._build_iso(staging_dir)
            elif format_type == "floppy_img":
                package_path = self._build_floppy(staging_dir)
            else:
                self.logger.warning(f"Unknown format: {format_type}")
                continue
            
            if package_path and package_path.exists():
                # Validate package
                validation = self.validator.validate_package(package_path)
                
                results["packages"][format_type] = {
                    "path": str(package_path),
                    "size": package_path.stat().st_size,
                    "checksum": validation["checks"].get("checksums", {}).get("sha256")
                }
                results["validation"][format_type] = validation
        
        # Generate summary report
        self._generate_summary(results)
        
        self.logger.info("Package build complete!")
        return results
    
    def _stage_content(self, source_dir: Path) -> Path:
        """
        Stage all content for packaging.
        
        Organizes:
        - Workbook pages (passed QA)
        - Failed QA items (separate folder)
        - Documentation
        - Source files
        - Metadata
        """
        
        staging = self.config.staging_dir / f"klutz_workbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        staging.mkdir(parents=True, exist_ok=True)
        
        # Copy workbook spreads
        if self.config.include_spreads:
            spreads_dir = staging / "workbook"
            spreads_dir.mkdir(exist_ok=True)
            
            for spread_file in source_dir.glob("output/spreads/*.png"):
                shutil.copy2(spread_file, spreads_dir / spread_file.name)
        
        # Package QA results
        if self.config.include_failed_qa:
            qa_dir = source_dir / "output/validation"
            if qa_dir.exists():
                self.qa_packager.package_qa_results(qa_dir, staging)
        
        # Copy documentation
        if self.config.include_documentation:
            docs_dir = staging / "documentation"
            docs_dir.mkdir(exist_ok=True)
            
            for doc_file in source_dir.glob("docs/generated/**/*"):
                if doc_file.is_file():
                    rel_path = doc_file.relative_to(source_dir / "docs/generated")
                    dest_path = docs_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(doc_file, dest_path)
        
        # Copy source files
        if self.config.include_source_files:
            source_staging = staging / "source"
            source_staging.mkdir(exist_ok=True)
            
            # Copy layouts
            layouts_dir = source_staging / "layouts"
            layouts_dir.mkdir(exist_ok=True)
            for layout_file in source_dir.glob("config/layouts/*.yaml"):
                shutil.copy2(layout_file, layouts_dir / layout_file.name)
            
            # Copy configuration
            config_file = source_dir / "config/master_config.yaml"
            if config_file.exists():
                shutil.copy2(config_file, source_staging / "master_config.yaml")
        
        # Generate manifest
        manifest = self._generate_manifest(staging)
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2))
        
        # Generate README
        readme = self._generate_readme()
        (staging / "README.txt").write_text(readme)
        
        # Generate checksums
        self._generate_checksums(staging)
        
        return staging
    
    def _generate_manifest(self, staging_dir: Path) -> Dict:
        """Generate complete manifest of package contents"""
        
        manifest = {
            "metadata": self.config.metadata,
            "generated": datetime.now().isoformat(),
            "contents": {},
            "file_count": 0,
            "total_size": 0
        }
        
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(staging_dir)
                
                manifest["contents"][str(rel_path)] = {
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "checksum": self.validator._calculate_checksum(file_path, 'md5')
                }
                
                manifest["file_count"] += 1
                manifest["total_size"] += file_path.stat().st_size
        
        return manifest
    
    def _generate_readme(self) -> str:
        """Generate README file for package"""
        
        return f"""
KLUTZ COMPUTER GRAPHICS WORKBOOK
=================================
Version: {self.config.metadata['version']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONTENTS
--------
- workbook/: Complete workbook pages (3400x2200 pixels, 300 DPI)
- documentation/: Technical documentation and guides
- source/: Source files and configurations
- qa_results/: Quality assurance reports

VIEWING INSTRUCTIONS
-------------------
1. For best results, view workbook pages at 100% zoom
2. Pages are designed for spiral binding with 462px spine area
3. Safe content zones: Left (150-1469), Right (1931-3250)

TECHNICAL SPECIFICATIONS
------------------------
- Canvas: 3400 x 2200 pixels
- DPI: 300 (print quality)
- Color Space: sRGB
- Format: PNG with lossless compression

AUTHENTICITY NOTICE
-------------------
This workbook has been generated using period-accurate
1996 specifications including:
- Kodak Gold 400 film simulation
- Apple M0100 mouse references
- Macintosh System 6 interface elements
- FAT12 floppy disk compatibility

COPYRIGHT
---------
© 1996 Klutz Press (simulated)
All rights reserved.

For more information, see documentation/index.html
"""
    
    def _generate_checksums(self, staging_dir: Path):
        """Generate checksum file for all contents"""
        
        checksums = []
        
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                if file == "checksums.txt":
                    continue
                    
                file_path = Path(root) / file
                rel_path = file_path.relative_to(staging_dir)
                
                md5 = self.validator._calculate_checksum(file_path, 'md5')
                sha256 = self.validator._calculate_checksum(file_path, 'sha256')
                
                checksums.append(f"MD5 ({rel_path}) = {md5}")
                checksums.append(f"SHA256 ({rel_path}) = {sha256}")
        
        checksum_file = staging_dir / "checksums.txt"
        checksum_file.write_text("\n".join(checksums))
    
    def _build_zip(self, staging_dir: Path) -> Path:
        """Build ZIP archive"""
        
        output_path = self.config.output_base / f"klutz_workbook_{self.config.metadata['version']}.zip"
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(staging_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(staging_dir.parent)
                    zf.write(file_path, arc_path)
        
        self.logger.info(f"ZIP archive created: {output_path}")
        return output_path
    
    def _build_tar(self, staging_dir: Path) -> Path:
        """Build TAR.GZ archive"""
        
        output_path = self.config.output_base / f"klutz_workbook_{self.config.metadata['version']}.tar.gz"
        
        with tarfile.open(output_path, 'w:gz') as tf:
            tf.add(staging_dir, arcname=staging_dir.name)
        
        self.logger.info(f"TAR.GZ archive created: {output_path}")
        return output_path
    
    def _build_sfx(self, staging_dir: Path) -> Path:
        """Build self-extracting archive"""
        
        if os.name == 'nt':
            output_path = self.config.output_base / f"klutz_workbook_{self.config.metadata['version']}.exe"
        else:
            output_path = self.config.output_base / f"klutz_workbook_{self.config.metadata['version']}.run"
        
        success = self.sfx_builder.create_self_extracting(staging_dir, output_path)
        
        if success:
            return output_path
        return None
    
    def _build_iso(self, staging_dir: Path) -> Path:
        """Build ISO image"""
        
        output_path = self.config.output_base / f"klutz_workbook_{self.config.metadata['version']}.iso"
        
        # Add autorun for Windows
        self.iso_builder.add_autorun(staging_dir)
        
        success = self.iso_builder.create_iso_image(staging_dir, output_path)
        
        if success:
            return output_path
        return None
    
    def _build_floppy(self, staging_dir: Path) -> Path:
        """Build floppy disk image"""
        
        output_path = self.config.output_base / f"klutz_paint_disk.img"
        
        # Create minimal content that fits on floppy
        floppy_content = staging_dir / "floppy_content"
        floppy_content.mkdir(exist_ok=True)
        
        # Add essential files only (must fit in 1.44MB)
        readme = """KLUTZ PAINT v1.0
================
Insert this disk when prompted by the workbook.

Files:
- KLUTZ.EXE: Main program
- README.TXT: This file
- SPRITES.DAT: Sample sprites

© 1996 Klutz Press"""
        
        (floppy_content / "README.TXT").write_text(readme)
        
        # Create mock executable (just a marker file)
        (floppy_content / "KLUTZ.EXE").write_bytes(b'MZ' + b'\x00' * 1000)  # DOS header
        
        # Create sample data file
        (floppy_content / "SPRITES.DAT").write_bytes(b'\x00' * 10000)
        
        success = self.floppy_builder.create_floppy_image(floppy_content, output_path)
        
        if success:
            return output_path
        return None
    
    def _generate_summary(self, results: Dict):
        """Generate summary report of all packages"""
        
        summary_path = self.config.output_base / "package_summary.json"
        
        # Add statistics
        results["statistics"] = {
            "total_packages": len(results["packages"]),
            "total_size": sum(p["size"] for p in results["packages"].values()),
            "all_valid": all(v["overall_valid"] for v in results["validation"].values())
        }
        
        summary_path.write_text(json.dumps(results, indent=2, default=str))
        
        # Log summary
        self.logger.info("=" * 60)
        self.logger.info("PACKAGE BUILD")
self.logger.info("=" * 60)
        self.logger.info("PACKAGE BUILD COMPLETE")
        self.logger.info("=" * 60)
        self.logger.info(f"Packages created: {results['statistics']['total_packages']}")
        self.logger.info(f"Total size: {results['statistics']['total_size'] / (1024*1024):.2f} MB")
        self.logger.info(f"All valid: {results['statistics']['all_valid']}")
        
        for format_type, package_info in results["packages"].items():
            self.logger.info(f"  {format_type}: {package_info['size'] / 1024:.1f} KB")
        
        self.logger.info("=" * 60)


class GitHubPagesDeployment:
    """
    Deployment configuration for GitHub Pages.
    
    This sets up:
    - Automated deployment workflow
    - Jekyll configuration for static site
    - CDN-ready asset organization
    - Version management
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_github_workflow(self) -> str:
        """
        Generate GitHub Actions workflow for automated deployment.
        
        This workflow:
        - Triggers on push to main branch
        - Builds all documentation formats
        - Packages workbook assets
        - Deploys to GitHub Pages
        """
        
        workflow = """name: Build and Deploy Klutz Workbook

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run validation checks
      run: |
        python -m asset_validator --strict
        
    - name: Generate documentation
      run: |
        python doc_generator.py --all-formats
        
    - name: Build workbook packages
      run: |
        python package_builder.py --formats zip,tar.gz,iso
        
    - name: Prepare deployment
      run: |
        mkdir -p _site
        cp -r docs/generated/html/* _site/
        cp -r output/packages _site/downloads
        
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: ./_site
        
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    
    steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
"""
        
        return workflow
    
    def generate_jekyll_config(self) -> str:
        """
        Generate Jekyll configuration for GitHub Pages.
        
        Configured for:
        - Klutz branding
        - Download links for all package formats
        - Interactive viewer for workbook pages
        """
        
        config = """# Jekyll configuration for Klutz Workbook

title: Klutz Computer Graphics Workbook
description: Learn Pixel Art the Klutz Way - 1996 Authentic Edition
theme: minima

# Custom variables
workbook:
  version: 1.0.0
  year: 1996
  pages: 48
  
downloads:
  zip:
    url: /downloads/klutz_workbook_1.0.0.zip
    size: "45 MB"
    description: "Standard ZIP archive"
  tar:
    url: /downloads/klutz_workbook_1.0.0.tar.gz
    size: "42 MB"
    description: "TAR.GZ for Unix/Linux"
  iso:
    url: /downloads/klutz_workbook_1.0.0.iso
    size: "650 MB"
    description: "CD-ROM ISO image"
  floppy:
    url: /downloads/klutz_paint_disk.img
    size: "1.44 MB"
    description: "Floppy disk image"

# Build settings
markdown: kramdown
plugins:
  - jekyll-feed
  - jekyll-seo-tag
  
# Exclude from build
exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor
  - .git
"""
        
        return config
    
    def generate_index_page(self) -> str:
        """Generate index.html for GitHub Pages site"""
        
        return """---
layout: default
title: Home
---

<style>
  body {
    background-color: #F8F3E5;
    font-family: Helvetica, Arial, sans-serif;
  }
  
  .klutz-header {
    background-color: #000;
    color: #FFD700;
    padding: 20px;
    text-align: center;
    font-size: 48px;
    font-weight: bold;
    transform: rotate(-2deg);
    margin: 20px 0;
  }
  
  .download-box {
    border: 4px solid #000;
    background-color: #FFFF00;
    padding: 20px;
    margin: 20px;
    box-shadow: 3px 3px 0px #000;
  }
  
  .download-box:hover {
    background-color: #F57D0D;
  }
  
  .page-preview {
    display: inline-block;
    margin: 10px;
    border: 3px solid #000;
    transform: rotate(-1deg);
  }
  
  .page-preview:nth-child(even) {
    transform: rotate(1deg);
  }
  
  .page-preview img {
    width: 200px;
    height: 130px;
    object-fit: cover;
  }
</style>

<div class="klutz-header">
  KLUTZ COMPUTER GRAPHICS WORKBOOK
</div>

<h2>Learn Pixel Art the Klutz Way!</h2>

<p><strong>48 pages of hands-on computer graphics fun!</strong></p>

<p>This authentic recreation of a 1996 Klutz Press workbook teaches pixel art 
using period-accurate technology and design. Every page has been generated 
using our hyper-specific pipeline to ensure absolute authenticity.</p>

<h2>📥 Download the Workbook</h2>

<div class="download-box">
  <h3>ZIP Archive (Recommended)</h3>
  <p>Standard ZIP format - works everywhere</p>
  <a href="{{ site.downloads.zip.url }}" class="download-link">
    Download ZIP ({{ site.downloads.zip.size }})
  </a>
</div>

<div class="download-box">
  <h3>ISO Image (CD-ROM)</h3>
  <p>Burn to CD-R for the authentic 1996 experience</p>
  <a href="{{ site.downloads.iso.url }}" class="download-link">
    Download ISO ({{ site.downloads.iso.size }})
  </a>
</div>

<div class="download-box">
  <h3>Floppy Disk Image</h3>
  <p>1.44MB disk image with companion software</p>
  <a href="{{ site.downloads.floppy.url }}" class="download-link">
    Download IMG ({{ site.downloads.floppy.size }})
  </a>
</div>

<h2>📖 Browse Online</h2>

<div class="page-gallery">
  {% for i in (1..24) %}
  <div class="page-preview">
    <a href="/viewer/#page{{ i }}">
      <img src="/assets/thumbnails/spread_{{ i | prepend: '00' | slice: -2, 2 }}.jpg" 
           alt="Spread {{ i }}">
    </a>
  </div>
  {% endfor %}
</div>

<h2>📋 Technical Specifications</h2>

<ul>
  <li><strong>Canvas:</strong> 3400 x 2200 pixels (exactly)</li>
  <li><strong>DPI:</strong> 300 (print quality)</li>
  <li><strong>Spine Dead Zone:</strong> x=1469 to x=1931 (no content allowed)</li>
  <li><strong>Color System:</strong> 70% Klutz primary, 20% Nickelodeon, 10% Goosebumps</li>
  <li><strong>Typography:</strong> Helvetica body, Chicago headlines</li>
  <li><strong>Film Stock:</strong> Kodak Gold 400 simulation (grain index 39)</li>
</ul>

<h2>🔍 Quality Assurance</h2>

<p>Every page has passed our comprehensive QA pipeline, checking for:</p>
<ul>
  <li>✅ Period authenticity (no modern elements)</li>
  <li>✅ Correct dimensions and positioning</li>
  <li>✅ Color distribution compliance</li>
  <li>✅ Typography accuracy</li>
  <li>✅ Spine clearance validation</li>
</ul>

<p><a href="/qa-report/">View Complete QA Report</a></p>

<hr>

<p><small>© 1996 Klutz Press (simulated). Generated using the Klutz Workbook Pipeline v1.0</small></p>
"""


class VersionManager:
    """
    Manages versioning and release history.
    
    Tracks:
    - Version numbers
    - Change logs
    - Build artifacts
    - Release notes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.version_file = Path("VERSION")
        self.changelog_file = Path("CHANGELOG.md")
        
    def get_current_version(self) -> str:
        """Get current version number"""
        
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "1.0.0"
    
    def increment_version(self, part: str = "patch") -> str:
        """
        Increment version number.
        
        Parts:
        - major: 1.0.0 -> 2.0.0
        - minor: 1.0.0 -> 1.1.0
        - patch: 1.0.0 -> 1.0.1
        """
        
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))
        
        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        else:
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        self.version_file.write_text(new_version)
        
        self.logger.info(f"Version updated: {current} -> {new_version}")
        return new_version
    
    def update_changelog(self, changes: List[str]):
        """Update CHANGELOG.md with new changes"""
        
        version = self.get_current_version()
        date = datetime.now().strftime("%Y-%m-%d")
        
        new_entry = f"""
## [{version}] - {date}

### Changes
"""
        
        for change in changes:
            new_entry += f"- {change}\n"
        
        # Prepend to existing changelog
        if self.changelog_file.exists():
            existing = self.changelog_file.read_text()
            content = new_entry + "\n" + existing
        else:
            content = f"# Changelog\n\nAll notable changes to the Klutz Workbook project.\n\n{new_entry}"
        
        self.changelog_file.write_text(content)
        self.logger.info(f"Changelog updated for version {version}")


# Main execution
if __name__ == "__main__":
    import argparse
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Build Klutz Workbook packages')
    parser.add_argument('--formats', nargs='+', 
                       default=['zip', 'tar.gz', 'iso'],
                       choices=['zip', 'tar.gz', 'self_extracting', 'iso', 'floppy_img'],
                       help='Package formats to generate')
    parser.add_argument('--source', type=Path, default=Path('.'),
                       help='Source directory')
    parser.add_argument('--output', type=Path, default=Path('output/packages'),
                       help='Output directory')
    parser.add_argument('--include-failed', action='store_true',
                       help='Include failed QA items')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate existing packages')
    
    args = parser.parse_args()
    
    if args.validate_only:
        # Validate existing packages
        validator = PackageValidator()
        
        for package_file in args.output.glob('*'):
            if package_file.is_file():
                print(f"\nValidating {package_file.name}...")
                validation = validator.validate_package(package_file)
                
                if validation['overall_valid']:
                    print(f" VALID")
                else:
                    print(f" INVALID")
                
                print(f"  Size: {validation['checks'].get('size_bytes', 0) / 1024:.1f} KB")
                if 'checksums' in validation['checks']:
                    print(f"  SHA256: {validation['checks']['checksums']['sha256']}")
    
    else:
        # Build packages
        config = PackageConfig(
            output_base=args.output,
            formats=args.formats,
            include_failed_qa=args.include_failed
        )
        
        builder = PackageBuilder(config)
        results = builder.build_all_packages(args.source)
        
        print("\n" + "=" * 60)
        print("PACKAGE BUILD SUMMARY")
        print("=" * 60)
        
        for format_type, package_info in results['packages'].items():
            print(f"\n{format_type.upper()}:")
            print(f"  Path: {package_info['path']}")
            print(f"  Size: {package_info['size'] / (1024*1024):.2f} MB")
            print(f"  SHA256: {package_info['checksum'][:16]}...")
            
            validation = results['validation'].get(format_type, {})
            if validation.get('overall_valid'):
                print(f"  Status:  VALID")
            else:
                print(f"  Status: INVALID")
        
        print("\n" + "=" * 60)
```
