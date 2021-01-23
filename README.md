#Output with default template:
![sample-out](https://user-images.githubusercontent.com/219793/105286709-243c3380-5bb7-11eb-9114-e788e098353d.png)

# External dependency:
- pdflatex (for most distribution it will be in ```texlive-core package```)
- texlive package with ```graphicx``` component (most likely ```texlive-pictures```)

# Linux and MacOS:
###Test install
Create virtual environment
```python -m venv venv``` then ```source venv/bin/activate``` 
and finally install with ```python setup.py install```

###Test run
Being in virtual environment execute ```python example/usage.py -i config.json```
to received pdf

# Windows:
**Not supported**
