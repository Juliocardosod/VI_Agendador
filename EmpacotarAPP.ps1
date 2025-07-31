venv38\Scripts\activate
pyinstaller --clean --onedir --distpath legacyDist --icon=icon.ico --contents-directory "." --uac-admin --noconfirm  app.py