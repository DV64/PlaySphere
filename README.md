# 🎮 PlaySphere 

<div align="center">
  <br>
  <p><strong>Advanced Game Search Engine</strong></p>
</div>

---

### 📋 Overview

PlaySphere is an advanced game search engine that allows users to search across multiple game sources simultaneously. It aggregates results from more than 8 different game repositories, providing a unified search experience with a modern, responsive interface.

### ✨ Features

- **Multi-source Search**: Search across 8+ game repositories at once
- **Source Filtering**: Choose which sources to include in your search
- **Bilingual Support**: Full Arabic and English language support
- **Responsive Design**: Works perfectly on all devices
- **Advanced Sorting**: Sort results by title, source, or date
- **Modern UI**: Beautiful, user-friendly interface with dark mode

### 🛠️ Project Components

The project consists of two main parts:

1. **Frontend**: HTML/CSS/JavaScript files that provide the user interface
   - `index.html`: Main application with responsive UI
   - `assets/`: Directory containing images, CSS, and JavaScript files

2. **Backend**: Python Flask server that handles the search requests
   - `server.py`: The main server application with search functionality
   - `translations_ar.py`: Arabic language translations
   - `translations_en.py`: English language translations

### 🔧 How to Run PlaySphere

#### Prerequisites

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)

#### Setup and Run

1. **Clone or download the project files**

2. **Create and activate a virtual environment**:
   ```bash
   # For Windows
   python -m venv venv
   venv\Scripts\activate

   # For macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   python server.py
   ```

5. **Access the application**:
   Open your browser and navigate to http://localhost:5000

### 💻 How to Use

1. **Select Game Sources**: Use the checkboxes to select which game repositories you want to search
2. **Enter Search Query**: Type your game title in the search box
3. **Start Search**: Click the search button or press Enter
4. **Browse Results**: View the unified search results from all selected sources
5. **Sort Results**: Use the sort options to organize results by title, source, or date
6. **Switch Language**: Toggle between Arabic and English using the language button

### 📂 Project Structure

```
PlaySphere/
├── assets/                 # Static assets (images, icons, CSS, JS)
├── .vscode/                # VS Code configuration
├── .gitignore              # Git ignore rules
├── index.html              # Main frontend HTML file
├── README.md               # Documentation file
├── requirements.txt        # Python dependencies
├── server.py               # Main server application
├── translations_ar.py      # Arabic translations
└── translations_en.py      # English translations
```

### 🔄 Server API

The server provides two main API endpoints:

- **GET /search**: Searches across game sources
  - Parameters: `q` (query), `sources` (comma-separated list of sources)
  - Example: `/search?q=minecraft&sources=fitgirl,ocean`

- **GET /translations**: Fetches UI translations
  - Parameters: `lang` (ar or en)
  - Example: `/translations?lang=ar`

### 📝 License

This project is licensed under the GNU General Public License (GPL) - a free, copyleft license for software that guarantees end users the freedom to run, study, share, and modify the software. For more information, visit [GNU GPL website](https://www.gnu.org/licenses/gpl-3.0.html).

### ⚠️ Disclaimer

This project is for educational purposes only. The developers are not responsible for any misuse of this application. PlaySphere simply aggregates search results from various sources and does not host any game files. Users are responsible for ensuring they comply with all applicable laws and regulations in their jurisdiction regarding game downloads and usage.
