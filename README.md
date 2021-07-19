# Generisanje Web aplikacije pomoću jezika specifičnog za domen

## Prerequisites
- Python 3
- pip

## Installation
- Install dependencies: `pip install -r requirements.txt`
- Install project packages (includes installing language and generator to textx):
    - on Windows run `install.bat`
    - on Linux run `install.sh`

## Run generator
Run command `degenerate`

or

Run command `textx generate --output-path $OUTPUT_PATH --target javascript --model_path $MODEL_PATH $MODEL_PATH`

Arguments:
- `-m [path]` path to application model file (.dgdl)
- `-s [path]` path to generated application source directory

Examples:
- `degenerate -m ./ExampleApp/application.dgdl -s ./ExampleApp/srcgen`
- `textx generate --output-path ./ExampleApp/srcdgen --target javascript --model_path ./ExampleApp/application.dgdl ./ExampleApp/application.dgdl`

## DSL Documentation
Documantation is available as a web application 
- From ./Documentation run `python app.py`
- In browser open `http://localhost:6325/`

Example application model can be found in ./ExampleApp/application.dgdl

## Features

**Bolded** features are implemented.

### Must have
- **Entiteti i veze medju entitetima**
- **CRUD backend aplikacija**(Python ili **Node.js**)
- **Servisi i model frontend aplikacije** (Angular ili **React**)
- **SQLite**
- **Odvajanje generisanog koda od korisničkog (apstraktne i nasleđene klase)**
### Nice to have
- **ACL**, sa definisanjem rola i pristupima
- Napredni *endpoint*-ovi (Nalik JPA)
- **Arhitektura zasnovana na *plugin*-ima**
- **Search, filter, pagining, sort kroz query parametre**
- **Generisanje komentara**
### Cound have
- **Dokumentcija generisanog API-ja**
- Izbor tehnologije za backend/frontend aplikaciju
### Won't have
- Grafički editor za JSD
- Plugin za VScode