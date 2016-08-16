# AstPhotos
A static single-page photo gallery website generator

***The README file is still under construction...***

## Get started
* Put your photos/images under `/src/img/[album_name]`
2. Run `python gen.py`
3. You have got the static webpage under `/out`! Put them in your static website host and enjoy it!

## Configure
- Edit `config_overridde.py` file base on `config_default.py`
- Create `/src/img/_site.json`, write and save:
```json
{
  "title": "anthony.f",
  "des": "photography",
  "me": "anthony",
  "me_link": "https://antnf.com"
}
```
- Create `/src/img/[album_name]/_album.json`, write and save:
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
- [ ] Template/theme support
- [ ] CLI support
- [ ] Js Modulize
- [ ] Use EXIF-Thumbail to calc default color
