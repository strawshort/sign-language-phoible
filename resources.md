# Resources

This file collects external references used to inform and support the development of this project or assist with ongoing implementation and design.

## Abbreviations and Common Terms  
Quick reference for terms, transcription formats, and symbol conventions used in sign language notation systems. 
_Terms refer to general concepts (e.g., code point, glyph, etc.), 
transcription formats refer to notation systems (i.e., HamNoSys, SWU, FSW, ISWA, etc.), 
and symbol conventions refer to the structure and format of identifiers (e.g., S144, U+40001, etc.)._

- **SWU – SignWriting in Unicode**  
  - a system that uses characters from a Unicode range set aside for SignWriting (called Plane 4)  
  - standard notation is `U+40001`, where `U` = Unicode, number in hexadecimal (base-16) = code point  
  - each code point represents a **SignWriting symbol** (displayed as a glyph using a SignWriting font)  
  - each symbol also has a descriptive Unicode name (e.g. `SIGNWRITING HAND-FIST INDEX`)

- **FSW – Formal SignWriting in ASCII**  
  - a plain-text system for writing SignWriting symbols using ASCII characters  
  - each symbol is identified by a **FSW symbol key**, written as `S` + hexadecimal ID (e.g. `S144`)  
  - full sign strings include symbol keys (e.g. `S144`, `S205`) and spatial coordinates (e.g. `x500`)  
  - example: `AS144S205x500S2dfx480`  
  - FSW code can be interpreted by a renderer to produce a glyph, typically as an image (e.g. SVG or PNG)

- **ISWA – International SignWriting Alphabet**  
  - a catalog of all SignWriting symbols organized into numeric codes  
  - example code: `01-04-001-01`, where:  
    - `01` = symbol group (e.g. handshapes)  
    - `04` = subgroup  
    - `001` = symbol ID  
    - `01` = variation (e.g. fill or rotation)
  
- **HamNoSys – Hamburg Notation System**  
  - a phonetic transcription system for encoding articulatory features using a linear string-based format 
  - notation is written as a comma-separated string (e.g. `hamfist,hamwristup,hammoveforward`)  
  - strings can be interpreted by a renderer to display a corresponding symbol sequence

## Tutorials on Notation Systems

- [Tutorial on HamNoSys by Annu Rani, Ph.D. Scholar, Punjabi University Patiala (YouTube)](https://youtu.be/iri8-T1Xn3w?feature=shared)
  to learn how HamNoSys represents handshapes and other phonological parameters  

- [SignWriting Symbol Lessons](https://www.signwriting.org/lessons/iswa/)
  to learn what handshape each SignWriting symbol represents, including its name, ISWA code, and a photo of the real, human handshape it corresponds to

## SignWriting Tools

- [Sutton SignWriting Character Index](https://slevinski.github.io/SuttonSignWriting/characters/index.html)
  to look up SignWriting symbols by typing their FSW code, and view their SWU, SVG, and PNG representations

- [SignMaker 2017](https://www.signbank.org/signmaker/#?ui=en)
  to build and edit full signs by combining SignWriting symbols in a visual editor that outputs SWU strings

- [SignWriting Character Viewer v2](https://slevinski.github.io/SignWriting_Character_Viewer/SignWriting_Character_Viewer_2.html#?ui=en&set=key)
  to look up symbols using a visual index
  (a table arranged by FSW key or Unicode code point, showing each SWU-font-rendered glyph and Unicode name)

## HamNoSys Tools

- [HamNoSys Input Tool](https://www.sign-lang.uni-hamburg.de/hamnosys/input/)
  to compose a transcription visually by selecting symbols
  (organized by handshape, orientation, location, movement, and two-handed features) in a panel
  and export it as a HamNoSys string


## Other Notation Systems

- **Symbol Font for ASL (GitHub)**,
  [Handshapes](https://aslfont.github.io/Symbol-Font-For-ASL/asl/handshapes.html),
  [Palm Orientation](https://aslfont.github.io/Symbol-Font-For-ASL/asl/palm-orientation.html),
  [Locations](https://aslfont.github.io/Symbol-Font-For-ASL/asl/locations.html),
  [Ways to Write (Notation Systems)](https://aslfont.github.io/Symbol-Font-For-ASL/ways-to-write.html)
  to compare how ASL handshapes, palm orientations, and locations are represented across multiple writing systems (e.g., SignWriting, HamNoSys, Stokoe, si5s);
  includes visual comparison tables and an overview of each notation system
