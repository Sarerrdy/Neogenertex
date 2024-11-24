# Neogenertex

This project is a self-service kiosk cyber cafe app built with Python, Kivy, and Flask. It supports internet access on demand, printing, scanning, and photocopying services. The app runs on Ubuntu on a Raspberry Pi in kiosk mode.

## Project Structure

- `backend/`: Contains the Flask server for backend operations.
- `frontend/`: Contains the Kivy app for frontend user interactions.
- `kv/`: Contains Kivy language files.
- `resources/`: Contains media resources such as advert videos.

## Installation

### Backend

```bash
cd backend
pipenv install
pipenv shell
python app.py
```
