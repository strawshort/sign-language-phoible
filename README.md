# SIGNIBLE

A **Sign Language Information Base and Linguistic Elements** repository.

SIGNIBLE is a cross-linguistic resource for sign language data centered on the 
linguistic elements of sign languages. 

This repository began as **Sign Language Phoible**, 
an ongoing effort to adapt the structure of the [PHOIBLE](https://phoible.org/) 
phonological inventory database to sign languages. The original goal was to 
develop a structured, extensible, and linguistically informed database of sign language phonologies, 
modeled on PHOIBLE's organization but adapted for the unique properties of sign languages.

The project has since expanded into [SIGNIBLE](https://strawshort.github.io/sign-language-phoible/), 
a broader framework for documenting, structuring, and comparing sign language data 
through the exploration of linguistic elements:

- **Linguistic elements** are the main components of sign language structure (e.g. handshape, non-manual features, etc.).
- **Segments** are specific units within those linguistic elements (e.g. each individual handshape).
- **Inventories** are collections of segments pertaining to a sign language entry within a dataset.
- **Notation systems** are the way the linguistic elements and segments are represented.

The current data centers on handshape segments, but additional elements will be considered in the future.

## Languages and Data

The repository currently includes data from two main sources: manually collected handshape 
inventories from Longqian Ming’s 2024 dataset and automatically extracted SignPuddle-derived data.

### Original handshape inventories

Inventories for twelve sign languages were manually collected and annotated by Longqian Ming in her [2024 unpublished report](Longqian_Ming_2024.pdf):

>[Longqian Ming (2024). *A Cross-Linguistic Collection of Handshapes from 12 Public Sign Language Resources*.] Unpublished report.

These inventories included handshape data for:

- American Sign Language (ASL)
- Australian Sign Language (Auslan)
- British Sign Language (BSL)
- Chinese Sign Language (CSL)
- Danish Sign Language (DSL)
- German Sign Language (DGS)
- Hong Kong Sign Language (HKSL)
- Korean Sign Language (KSL)
- Netherlands Sign Language (NGT)
- New Zealand Sign Language (NZSL)
- Swedish Sign Language (SSL)
- Taiwan Sign Language (TSL)

The handshapes were identified through a visual analysis of publicly available sign language resources. 
The annotation process was based on visual classification of handshape forms, using the following notation systems:

- **HamNoSys**: Hamburg Notation System
- **FSW**: Formal SignWriting in ASCII
- **SignWriting** symbols

Where available, glosses and English translations were included.

The original dataset was compiled as a single table. For this repository, 
it was separated into one CSV file per language and reformatted as an inventory list of segments 
with notation data to enable cross-linguistic comparison.

### SignPuddle Inventories 

Handshape inventories were compiled from SignPuddle data by automatically extracting 
FSW strings from all available [SignPuddle](https://signbank.org/signpuddle/) dictionaries 
and identifying handshape segments in each entry. (Since the data reflects the original 
source entries, source-level inconsistencies or errors may still appear in the data.)

Because SignPuddle `sgn` identifiers could refer to a country or region rather than a sign language, 
identifying the dictionary languages required conducting a [manual mapping analysis](data/slphoible/mapping_sgn_to_glottocode_iso.csv). 
This analysis compared SignPuddle country-region identifiers with the sign languages listed 
in [Glottolog](https://glottolog.org) for the corresponding countries and regions. When the mapping was not direct, 
language status and use information from additional sources were also considered.

With this mapping in place, the following logic was used for SignPuddle dictionaries that do not identify a language directly:

- Where Glottolog lists only one sign language for a country or region, that language is assigned.
- Where majority and minority or endangered languages coexist, the main national language is assigned.
- Languages are combined if a country has more than one major sign language (i.e., Myanmar, Northern Ireland, and Vietnam).
- Languages not listed in Glottolog remain included and are marked as such.

## Repository Structure

| Path | Description |
|---|---|
| `data/longqian2024/` | Longqian Ming handshape inventory data |
| `data/signpuddle/` | SignPuddle raw data files and resulting inventories |
| `data/slphoible/` | Main CSV tables used to generate the main website pages |
| `docs/` | Generated website pages |
| `scripts/pages/` | Scripts for generating website pages |
| `scripts/signpuddle/` | Scripts for extracting and processing SignPuddle data |
| `resources.md` | Resources used for notation systems and sign language data |

## Project Scope and Future Work

This repository is in active development. Future work may include:

- Expansion to more sign languages
- Inclusion of additional linguistic elements beyond handshape segments
- Semi-automated or automated extraction of additional parameters
- Further development of notation-system metadata

No formal versioned release has been created yet.

## License and Use

This project is in early development and does not yet have a formal license. Please contact the authors in advance for citation guidance, data reuse, or collaboration inquiries.