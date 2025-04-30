
# Blockly Robot Companion

A warm, empathetic conversational agent embedded in a social robot. Designed primarily for elderly users, Blockly listens, talks, and moves to create a meaningful and engaging interaction.

---

## Features

- Real-time speech-to-text and conversation with emotional reflection  
- Personalized user experience (name-based)  
- Robot body gestures paired with responses  
- Gemini language model integration for dynamic replies  

---

## Getting Started

### Prerequisites

- Python 3.8+
- [Poetry](https://python-poetry.org/) for managing dependencies and virtual environments  
- Internet connection (for Gemini API)  
- Access to a WAMP router  
- Alpha Mini robot  

---

## Installation

### Clone this repository:

```bash
git clone https://github.com/Niclas-J-M/HRI-Project.git
cd HRI-Project
```

---

## Running

You can also set up a virtual environment using Poetry. Poetry can be installed using pip:

```bash
pip install poetry
```

Then initiate the virtual environment with the required dependencies (see `poetry.lock`, `pyproject.toml`):

```bash
poetry config virtualenvs.in-project true    # ensures virtual environment is in project
poetry install
```

The virtual environment can be accessed from the shell using:

```bash
poetry shell
```

IDEs like PyCharm will be able to detect the interpreter of this virtual environment.

---

## Configuration

Before running the program, update two critical values in `main.py`:

### Gemini API Key

Replace the placeholder string in the following line with your actual Google Generative AI key:

```python
language_model = LanguageModel(api_key="GOOGLE API KEY")
```

### Robot Realm Key

Replace the realm placeholder with your robot's actual realm ID:

```python
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="REALM KEY"
)
```

---

## Starting the Program

Once everything is configured and the virtual environment is active, start the interaction system:

```bash
python main.py
```

Make sure:

- Your Alpha Mini robot is online and connected to the specified WAMP server (`ws://wamp.robotsindeklas.nl`)  
- You’ve set your **Google API Key** and **Realm Key** as described above  

---

## File Structure

```bash
.
├── alpha_mini.py           # Robot speech & movement interface
├── audio_processor.py      # Audio stream listener and silence detection
├── language_model.py       # Handles interactions with the Gemini language model
├── prompt.py               # Persona definition for the robot assistant
├── main.py                 # Main event loop and user interaction logic
├── pyproject.toml          # Poetry project configuration
├── poetry.lock             # Exact package versions
```

---

## Credits

- **Gemini API** – Powered by [Google Generative AI](https://ai.google.dev)  
- **Twisted & Autobahn** – For asynchronous communication with the robot  
- **Alpha Mini SDK** – For robot sensor, speech, and gesture control  