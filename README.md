FastAPI Service Template [Base]
===========================
This is a cookiecutter boilerplate based template for building FastAPI Rest Services for XXX AI solutions.
The template provides a boilerplate code to quickly begin building and deploying RestAPIs. They have multiple integrated functionalites such as Configuration management (Hydra), Database Storage (Mongo), OCR (Azure, Pytesseract)

[USAGE]
1. Generate the template
```python
cookiecutter https://github.com/XXX-AI/XXX-service-template-base.git
```
2. Fill in the details of the project.
3. Make configuration changes in: app/conf/config.yaml and its subfolder.
4. Make API changes for routes in: app/api and its files.
    - Add new routes categories.
    - Edit genrated routes as per your need.
5. Make changes to schemas in: app/schemas and its files.


[VERSIONS]
### v1.0.0 -> 2nd Aug 2022
### v2.0.0 -> 18th Jan 2023

[TODO]
- [ ] Lambda Integration
- [X] Generic Routes
    - [X] Internal Digitization API
    - [X] External Processing API
    - [X] Admin Routes
        - [X] Health API
        - [X] Info API - Service contract
        - [X] Ingestor Scheduler Control API
- [ ] Portal Generation
- [X] Docker Integration
- [ ] Makefile Integration
- [X] Factory Model
    - [X] Logger
    - [X] FastAPI
    - [X] Mongo 
    - [ ] PostgreSQL
- [X] OCR
    - [X] Local Pytesseract
    - [X] Azure Layout
    - [X] Azure Form Recognizer
    - [ ] AWS Textract
    - [ ] AWS Form Recognizer
    - [ ] PaddleOCR
- [X] Standardised Response Json
- [ ] LTM Integration
- [ ] Documentation
    - [X] Usage
    - [ ] Health Checks
    - [ ] Schema
    - [ ] OCR
    - [ ] Multiprocessing
