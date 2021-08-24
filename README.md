# Generating Web applications using a DSL

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
- **Entities and relationships**
- **CRUD backend app**(Python or **Node.js**)
- **Services and model for frontend app** (Angular or **React**)
- **SQLite**
- **Separating generated from user written code (abstract and inherited classes)**
### Nice to have
- **ACL**, with roles and access control
- Advanced *endpoints* (like JPA)
- **Arhitektura zasnovana na *plugin*-ima**
- ***Plugin* based architecture**
- **Search, filter, paging, sort through query parameters**
- **Comment generation**
### Could have
- **Dokumentcija generisanog API-ja**
- **Generated API documentation**
- Technology choice for backend/frontend apps
### Won't have
- GUI for DSL
- VSCode plugin