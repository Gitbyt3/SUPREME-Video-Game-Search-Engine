# SUPREME-Video-Game-Search-Engine  
**The SUPREME ULTIMATE Search Engine for Retrieving Video Games**

---

## How to Start

### 1. Install Python dependencies  
Make sure you have Python 3.12.0 installed. Then install the required packages:

```bash
pip install -r path/to/your/requirements.txt
```

Replace `path/to/your/requirements.txt` with the actual path on your system, for example:

```bash
pip install -r C:/Users/yourname/Downloads/SUPREME-Video-Game-Search-Engine/requirements.txt
```

Or manually install:

| Package         | Version    |
|----------------|------------|
| `numpy`        | 1.26.4     |
| `pandas`       | 2.2.3      |
| `scikit-learn` | 1.6.1      |
| `lightgbm`     | 4.6.0      |
| `sentence-transformers` | 4.0.2 |
| `faiss-cpu`    | 1.10.0     |
| `tqdm`         | 4.67.1     |
| `nltk`         | 3.9.1      |
| `rank_bm25`    | 0.2.2      |

---

### 2. Install Node.js  
[Download and install Node.js here](https://nodejs.org/en)

---

### 3. Run the app

#### On Windows:

Edit the .bat file (setup_and_run.bat):
:: Replace directories with the directory of your own Anaconda environment name (make sure it is the same environment the dependencies are installed on)

Example directory:
CALL C:\\Path\\To\\Anaconda3\\Scripts\\activate.bat your_env_name

Example of .bat file lines to change:
call npm install
start "" cmd /k "CALL C:\\Path\\To\\Anaconda3\\Scripts\\activate.bat your_env_name && npm start"
cd ..

After replacing, save & run:
```shell
setup_and_run.bat
```

#### On macOS / Linux:

```bash
./setup_and_run.sh
```

This will build and launch the backend and frontend services for the search engine.