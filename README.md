# News Intelligence System

A powerful news intelligence application that analyzes news headlines to identify top trending agencies and companies.

## 🚀 Features

- **Top Agencies Analysis**: Analyzes 100 news headlines to identify and rank top trending agencies/companies
- **News Headlines**: Fetches and displays latest news headlines with clean descriptions
- **Smart Entity Extraction**: Uses NLP to extract and rank entities by frequency
- **Download Options**: Export results as CSV or Excel
- **No API Key Required**: Works with Google News RSS (free, unlimited)

## 📊 How It Works

1. **Fetches** up to 100 news headlines from Google News RSS
2. **Analyzes** headlines using NLP to extract company/agency names
3. **Ranks** entities by frequency and relevance
4. **Displays** top 10 agencies with confidence scores

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/news-intelligence-system.git
cd news-intelligence-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app2.py
```

4. Open your browser and go to `http://localhost:8501`

## 📦 Dependencies

- streamlit
- beautifulsoup4
- feedparser
- requests
- pandas
- aiohttp
- python-docx
- xlsxwriter

See `requirements.txt` for complete list.

## 🎯 Usage

### Get Top Agencies List

1. Enter your keyword (e.g., "Electric Vehicles", "AI Industry")
2. Set duration (1-30 days)
3. Click **"Get Top Agencies List"**
4. View ranked list of top 10 agencies/companies
5. Download results as CSV

### Get News Headlines

1. Enter your keyword
2. Set duration
3. Click **"Get News Headlines"**
4. Browse all headlines with descriptions
5. Download as Excel or CSV

## 🌐 Deployment

### Deploy to Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Set main file: `app2.py`
7. Click "Deploy"

### Deploy to Heroku

1. Create `Procfile`:
```
web: streamlit run app2.py --server.port=$PORT
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Deploy to Railway

1. Connect your GitHub repo to Railway
2. Set start command: `streamlit run app2.py`
3. Deploy automatically

## 📁 Project Structure

```
news-intelligence-system/
├── app2.py                      # Main application
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git ignore file
├── Mavericks logo.png          # Logo (optional)
└── HYBRID_SETUP_GUIDE.md       # Setup guide
```

## 🎨 Features Breakdown

### Top Agencies Analysis
- Analyzes 100 headlines
- Extracts company/agency names using NLP
- Ranks by frequency
- Color-coded confidence scores:
  - 🟢 High (10%+ mentions)
  - 🟡 Medium (5-10% mentions)
  - 🟠 Low (<5% mentions)

### News Headlines
- Fetches up to 100 articles
- Clean, readable descriptions
- Source and date information
- Direct links to full articles

## 🔧 Configuration

No configuration needed! The app works out of the box with Google News RSS.

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions, please open an issue on GitHub.

## 🎉 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- News data from Google News RSS
- NLP-based entity extraction

---

**Made with ❤️ for news intelligence**
