# Synthetic Manuscript Generator

Automated Python pipeline for generating realistic synthetic historical manuscript folios for OCR and document-understanding research.

## Supported Scripts
- Devanagari
- Modi
- Sharada

## Dataset

300 manuscript images with matching Markdown ground-truth files.

| Script | Train | Validation | Test | Total |
|---|---:|---:|---:|---:|
| Devanagari | 85 | 10 | 5 | 100 |
| Modi | 85 | 10 | 5 | 100 |
| Sharada | 85 | 10 | 5 | 100 |
| Total | 255 | 30 | 15 | 300 |

## Dataset Structure

output/dataset/devanagari/train/
output/dataset/devanagari/validation/
output/dataset/devanagari/test/
output/dataset/modi/train/
output/dataset/modi/validation/
output/dataset/modi/test/
output/dataset/sharada/train/
output/dataset/sharada/validation/
output/dataset/sharada/test/

Each generated image has a matching .md annotation file.

## Usage

Run the generator with:

    python generate.py

## Requirements

Python 3.12+, Pillow, NumPy, OpenCV and PyYAML.

## Hugging Face Dataset

saniyameshram/synthetic-manuscript-generator`n
## Project Structure

- generate.py - main dataset generator
- server/ - backend application
- client/ - frontend application
- requirements.txt - Python dependencies
- README.md - project documentation

## Output

The generator produces synthetic manuscript PNG images and synchronized Markdown ground-truth annotations.

## Submission

Synthetic Manuscript Generator technical assignment for the ImmverseAI AIML Intern Role.
