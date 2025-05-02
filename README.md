# Sign Language Phoible

A cross-linguistic resource for sign language phonological inventories and features, modeled after PHOIBLE.

This repository is part of an ongoing effort to adapt the structure of the [Phoible](https://phoible.org/) phonological inventory database to sign languages. The goal of this project is to develop a structured, extensible, and linguistically informed database of sign language phonologies, modeled on Phoible's organization but adapted for the unique properties of signed languages.

While the current release focuses on handshape inventories, the broader project will eventually include other key phonological parameters such as movement, location, orientation, and non-manual features.

## Languages Included

This dataset includes handshape inventories for the following sign languages:

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

## About the Data

These inventories were manually collected and annotated by Longqian Ming and are based on her 2024 unpublished report:

> *Longqian Ming (2024). A Cross-Linguistic Collection of Handshapes from 12 Public Sign Language Resources* (unpublished).

The handshapes were identified through visual analysis of publicly available sign language resources. The annotation process was based on visual classification of handshape forms, using the following systems:

- **HamNoSys** (Hamburg Notation System)
- **Formal SignWriting (FSW)**
- **SignWriting**

Where available, glosses and English translations were included.

The original dataset was compiled as a single table. For this repository, it was adapted into one CSV file per language and reformatted to support cross-linguistic comparison and accessibility.

## Repository Structure

- `tables/` – CSV files, including:
  - One inventory per language
  - Combined inventories across all 12 languages (in multiple formats)
  - Prototype tables for "inventories", "languages", and "segments" (with placeholder data)

## Project Scope and Future Work

This repository represents the **initial manual phase** of the Sign Language Phoible project. Future work may include:

- Expansion to more sign languages
- Semi-automated or automated extraction of phonological parameters (e.g., using FSW)
- Inclusion of additional phonological parameters (e.g., movement, location, orientation)
- Addition of example media and metadata

## License and Use

This project is in early development and does not yet have a formal license. Please contact the authors in advance for citation guidance, data reuse, or collaboration inquiries.
