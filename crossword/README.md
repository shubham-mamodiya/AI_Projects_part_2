# AI Crossword Puzzle Generator

A Python-based crossword puzzle generator that uses artificial intelligence concepts like Constraint Satisfaction Problems (CSP) to create and solve crossword puzzles.

## 🚀 Features

- Generate crossword puzzles from custom grid structures
- Smart word placement using CSP algorithms
- Support for both across and down word placements
- Output puzzles to terminal or save as image files
- Uses arc consistency and backtracking for efficient solving

## 📋 Requirements

- Python 3.x
- Pillow (PIL) library: `pip install Pillow`
- OpenSans font (place in assets/fonts/)

## 🔧 Project Structure

```
crossword/
├── crossword.py      # Core crossword logic and classes
├── generate.py       # Puzzle generation and solving logic
├── assets/
│   └── fonts/       # Font files for image generation
├── data/
│   ├── structure/   # Crossword grid structure files
│   └── words/       # Word list files
└── README.md
```

## 🎯 TODO List

1. Add input validation for structure and word files
2. Implement better word selection heuristics
3. Add difficulty levels
4. Create more example structures
5. Add unit tests
6. Add word hints/clues support
7. Improve image output formatting
8. Add support for different languages

## 💻 Usage

```bash
python generate.py structure_file words_file [output_file]
```

Example:
```bash
python generate.py data/structure1.txt data/wordlist.txt puzzle.png
```

## 📝 Structure File Format

Use `_` for letter spaces and any other character for blocked cells:
```
___##___
__#_#___
___#____
##___###
____#___
___#_#__
___##___
```

## 🛠️ Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
