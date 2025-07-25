test_service (TEST) RestAPI
=========================================
xyz


**Note: This template is based on xxxAI Framework version 1.0.0**

Solution Flow Diagram
---------------------
![SLRD Model Diagram](imgs/dummy-flow.jpg)

Implementation
--------------
### Development Setup
Setup the conda environment and load the necessary requirements.
```python
conda create --name=TEST python=3.8
# accept all inputs
# Install requirements [Development]
pip install xxxai --extra-index-url https://__token__:PUT_TOKEN_VALUE_HERE@gitlab.com/api/v4/projects/31912870/packages/pypi/simple
pip install -r requirements-dev.txt
pip install -r requirements.txt

# Install requirements [Prd]
pip install -r requirements.txt
```

### Service Setup
Export environment variables
```shell
export APP_ACRONYM=TEST
export MODE=development
export CFG_KEY=KEY
export CFG_SECRET=Secret
```
```python
uvicorn app.TEST_app:app --reload --port 8123 --host 0.0.0.0
```
Open browser on url:
- http://server_ip:8123/docs  

Code changes made will be auto loaded for action.

[VERSIONS]
### v1.0.0 -> 2nd Aug 2022

[TODO]
- [ ] Feature-1
    - [x] Sub-Feature-1
    - [ ] Sub-Feature-2
- [x] Feature-1
- [ ] Feature-2
