# AstPhotos
A static single-page photo gallery website generator

***The README file is still under construction...***

## Get started

#### Interactive Editor
*The new Interactive Editor is now available!*
1. Run command `astphoto.py editor`
1. Open the browser and go to `http://localhost:81`
1. Create albums, add photos, modify photos' metadata easily!

#### CLI
1. `astphoto.py init Astphoto` *( you can replace "Astphoto" to the name you like )*
1. `astphoto.py create album "My Family"`
1. Copy your photos/images to `img/my_family/`
1. `astphoto.py gen`
1. You will get the complied static files under `complied/`! You can put them into your static website host and enjoy it!

## Configure

**Directory Structure:**
```
img
├── _site.json
├── about.md
└── Album_A
    ├── _album.json
    ├── A.jpg
    ├── B.jpg
    ├── C.jpg
    └── ...
```

- Edit `config_overridde.py` file base on `config_default.py`
- Create `/img/_site.json`, write and save:
```json
{
  "title": "anthony.f",
  "des": "photography",
  "me": "anthony",
  "me_link": "https://antnf.com"
}
```
- Create `/img/[album_name]/_album.json`, write and save:
```json
{
  "name": "Family",
  "des": "My family and I.",
  "photographer": "anthony.f",
  "location": "Hangzhou",
  "cover": "13.jpg",
  "photo_orderby": "shuffle"
}
```
- Regenerate the website

## Todos
- **CLI**
  - [ ] init [name]
  - [ ] gen -static -index
  - [x] clear
  - [ ] album [new|modify] [name]
  - [x] host
  - [ ] Interaction json generator

- **Generator**
  - [x] ~~Use EXIF-Thumbail to calc default color~~ Use random samples (for better performance)
  - [x] Folder copy
  - [x] Windows Unicode support
  - [x] Template/theme support
  - [x] Minify
  - [x] Markdown
  - [x] Overview
  - [ ] Thumbails
  - [x] Backgound set
  - [x] About portrait
  - [x] Photographer links dictionrary
  - [ ] Source->Target filepath table
  - [x] Image data's cache
  - [ ] ProgessBar / Logs
  - [x] Imporve infodict
  - [x] Logo support
  - [ ] Auto create root folder if not exists

- **Template**
  - [x] Javascripts decoupling
  - [x] Hash Router
  - [x] Horizontal / Vertical view auto switch
  - [x] Photo details toggle

- **Interactive Metadata Editor**
  - [x] Metadata Edit
  - [x] Photo uploading
  - [ ] Upload progress bar
  - [ ] New album
  - [ ] Update after uploads
  - [x] Reconsider UI
  - [ ] Configure settings in Editor
