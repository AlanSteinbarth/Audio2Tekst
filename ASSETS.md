# 📸 Audio2Tekst - Visual Assets

This directory contains visual assets for the Audio2Tekst project.

## 🎨 Current Assets Needed

### 1. **Logo & Branding**
- [ ] Main logo (SVG + PNG)
- [ ] Favicon (ICO + PNG)
- [ ] Social media banner (1200x630)

### 2. **Screenshots**
- [ ] Main interface (800x600)
- [ ] File upload process (800x600)
- [ ] Transcription in progress (800x600)
- [ ] Results display (800x600)
- [ ] Summary generation (800x600)
- [ ] System information panel (400x300)

### 3. **Demo Materials**
- [ ] Demo GIF (800x400, <5MB)
- [ ] Tutorial video (MP4, <10MB)
- [ ] Before/after comparison

### 4. **Architecture Diagrams**
- [ ] System architecture (PNG/SVG)
- [ ] Data flow diagram
- [ ] Process flowchart

## 🎯 Brand Colors

```css
Primary: #2E86AB (Blue)
Secondary: #A23B72 (Purple)
Accent: #F18F01 (Orange)
Success: #2ECC71 (Green)
Warning: #F39C12 (Yellow)
Error: #E74C3C (Red)
Background: #F8F9FA (Light Gray)
Text: #2C3E50 (Dark Blue)
```

## 📝 Asset Guidelines

1. **Screenshots**: 
   - Use high resolution (at least 1920x1080)
   - Crop to focus area
   - Consistent UI state (no errors, good data)

2. **Demo GIF**:
   - Show complete workflow: upload → transcribe → summarize
   - Keep under 5MB
   - Use tools like LICEcap or Kap

3. **Logo**:
   - Audio wave + text elements
   - Scalable SVG format
   - Transparent background version

## 🛠️ Tools Recommended

- **Screenshots**: macOS Screenshot (Cmd+Shift+4), Windows Snipping Tool
- **GIF Creation**: LICEcap, Kap, GIMP
- **Image Editing**: GIMP, Canva, Figma
- **Logo Design**: Figma, Canva, Adobe Illustrator

## 📁 File Structure

```
assets/
├── logo/
│   ├── logo.svg
│   ├── logo.png
│   ├── logo-light.png
│   └── favicon.ico
├── screenshots/
│   ├── main-interface.png
│   ├── transcription-process.png
│   ├── results-display.png
│   └── summary-generation.png
├── demo/
│   ├── demo.gif
│   └── tutorial.mp4
└── diagrams/
    ├── architecture.png
    └── data-flow.svg
```

## 🚀 Quick Asset Creation Commands

### Screenshot Optimization
```bash
# Compress PNG files
pngquant --quality=65-90 screenshot.png --output screenshot-compressed.png

# Convert to WebP for better compression
cwebp -q 85 screenshot.png -o screenshot.webp
```

### GIF Creation with FFmpeg
```bash
# Convert video to GIF
ffmpeg -i demo.mov -vf "fps=10,scale=800:-1:flags=lanczos" -c:v gif demo.gif

# Optimize GIF size
gifsicle -O3 --lossy=80 -o demo-optimized.gif demo.gif
```

## 📱 Social Media Specs

| Platform | Size | Format | Notes |
|----------|------|--------|-------|
| GitHub Social | 1200x630 | PNG/JPG | Repository preview |
| Twitter Card | 1200x675 | PNG/JPG | Tweet previews |
| LinkedIn | 1200x627 | PNG/JPG | Post sharing |
| Facebook | 1200x630 | PNG/JPG | Link previews |

---

*This file will be updated as assets are created and added to the repository.*
