# AstPhotos
A static single-page photo gallery website generator

***The README file is still under construction...***

## Get started
1. `gen.py init Astphoto` *( you can replace "Astphoto" to the name you like )*
1. `gen.py create album "My Family"`
1. Copy your photos/images to `img/my_family/`
1. `gen.py gen`
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

## Todo
- [x] Template/theme support
- [ ] CLI support
  - [ ] init [name]
  - [ ] gen -static -index
  - [x] clear
  - [ ] album [new|modify] [name]
  - [x] host
  - [ ] Interaction json generator
- [x] Javascripts decoupling
- [x] ~~Use EXIF-Thumbail to calc default color~~ Use random samples (for better performance)
- [x] Folder copy
- [x] Windows Unicode support
- [x] Hash Router
- [x] Minify
- [x] Markdown
- [x] About portrait
- [x] Backgound set
- [x] Photographer links dictionrary
- [x] Overview
- [x] Horizontal / Vertical view auto switch
- [ ] Thumbails
- [ ] Source->Target filepath table
- [x] Image data's cache
- [ ] ProgessBar / Logs
- [x] Imporve infodict
- [x] Photo details toggle
- [x] Logo support
- [x] Interactive Metadata Editor
