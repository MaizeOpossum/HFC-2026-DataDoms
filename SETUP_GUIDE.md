# COOL Dashboard Setup Guide

Welcome! This guide will help you set up and run the **COOL (Cooperative Optimisation of Urban Loads)** dashboard on your local machine. The dashboard visualizes a real-time energy trading marketplace between 50 buildings in Singapore, powered by AI agents.

---

## 🎯 What You'll See

Once running, the dashboard displays:
- **Live Singapore District Map**: 50 buildings colored by temperature, power, or grid stress
- **AI Agent Network**: Real-time visualization of energy trades between buildings
- **Carbon Counter**: Total CO₂ emissions saved through efficient energy trading
- **Market Statistics**: Live order book, trade history, and agent AI reasoning
- **Building Analytics**: Individual building metrics and performance over time

---

## 📋 Prerequisites

### Required
- **Python 3.10 or higher** ([Download here](https://www.python.org/downloads/))
- **Git** ([Download here](https://git-scm.com/downloads))
- **Terminal/Command Prompt** access

### Important: Virtual Environment
**⚠️ Using a virtual environment is strongly recommended** to avoid conflicts with system Python packages. This project uses modern dependencies that should be isolated from your system Python installation.

---

## 🚀 Step-by-Step Setup

### 1. Clone the Repository

Open your terminal and run:

```bash
git clone <your-github-repo-url>
cd "DataDoms HFC"
```

Replace `<your-github-repo-url>` with your actual GitHub repository URL.

---

### 2. Create a Virtual Environment ⚠️ REQUIRED

**Important:** Always use a virtual environment for this project. This keeps project dependencies isolated from your system Python and prevents conflicts.

**Option A: Using venv (Recommended - Built into Python)**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

**Option B: Using conda**
```bash
conda create -n cool python=3.11
conda activate cool
```

**Verify activation:** You should see `(venv)` or `(cool)` in your terminal prompt when activated. If you don't see this, the virtual environment is not active and you should activate it before proceeding.

---

### 3. Install Dependencies

**⚠️ Make sure your virtual environment is activated** (you should see `(venv)` in your prompt).

Install the project and its dependencies:

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install the project and all dependencies
pip install -e .
```

This installs:
- **Streamlit**: Dashboard framework
- **Pydantic**: Configuration management
- **FastAPI**: API backend
- **Plotly**: Interactive charts
- **PyDeck**: 3D map visualization
- **Pandas**: Data manipulation
- **Structlog**: Structured logging
- And more...

**Installation time:** 1-3 minutes depending on your internet speed.

**Note:** The dashboard uses **mock telemetry data** by default (simulated building data). Real-world data sources like CityLearn can be integrated in the future but are not required.

---

### 4. Configure Environment Variables

The project needs a `.env` file for configuration:

```bash
# Copy the example environment file
cp .env.example .env
```

**Optional:** Edit `.env` if you want to customize settings:
```bash
# Open in your favorite text editor
nano .env
# or
code .env
# or
vim .env
```

**Default settings work fine!** The only optional customization is the Mapbox token (for enhanced maps), but the dashboard works without it.

---

### 5. Launch the Dashboard

Run the dashboard with:

```bash
streamlit run thermal_commons_mvp/dashboard/app.py
```

**Or use the convenience command:**
```bash
cool-dash
```

You should see output like:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.X:8501
```

---

### 6. Open in Browser

The dashboard should automatically open in your default browser. If not, navigate to:

```
http://localhost:8501
```

🎉 **You should now see the COOL dashboard!**

---

## 🎮 Using the Dashboard

### Main Controls

1. **▶️ Start/Pause Simulation**
   - Located in the top-right corner
   - Starts the real-time trading simulation (3-second refresh intervals)

2. **Metric Selector**
   - Choose between "Temp.", "Power", or "Grid stress" to color the map
   - Updates map, gauges, and charts

3. **Building Selection**
   - Click on buildings in the map or select from dropdowns
   - View detailed analytics for specific buildings

### Dashboard Sections

**🗺️ District Map (Top)**
- Interactive 3D map of Singapore's commercial district
- 50 buildings colored by selected metric
- Zoom, pan, and rotate with mouse/trackpad

**🤖 AI Agent Network (Left)**
- Real-time visualization of energy trades
- Green nodes = buildings
- Arrows = trade flows (buyer → seller)
- Hover to see trade details and AI reasoning

**⚡ Carbon Counter (Right)**
- Total kWh saved through trading
- CO₂ emissions avoided (using Singapore grid carbon factor)
- Updates with each trade

**📊 Market Statistics (Middle)**
- Order book: current bids and asks
- Recent trades with prices
- AI agent reasoning for decisions

**📈 Building Analytics (Bottom)**
- Time-series charts for individual buildings
- Temperature, humidity, power, grid stress over time

---

## 🧠 Understanding the AI Agents

Each of the 50 buildings has an **agentic AI** that:

1. **Analyzes** multiple factors:
   - Building temperature and comfort
   - Current power load
   - Grid stress level (demand-response signal)
   - Historical trade performance

2. **Selects a strategy**:
   - **Aggressive**: High grid stress → maximize load shedding
   - **Conservative**: Comfortable conditions → minimal participation
   - **Opportunistic**: Learn from successful trades
   - **Adaptive**: Balance multiple factors

3. **Generates bids and asks**:
   - Bid = willingness to buy capacity
   - Ask = willingness to sell (shed load)

4. **Learns and adapts**:
   - Tracks last 50 trades
   - Adjusts strategy based on success rates

You can see the AI reasoning in the **Agent Network** section by hovering over trade arrows!

---

## 📊 Grid Stress Levels

The power grid stress cycles through 4 levels in a 4-minute loop (configurable):

- **🟢 LOW (0-25%)**: Value = 0.25, normal operations
- **🟡 MEDIUM (25-50%)**: Value = 0.5, moderate stress
- **🔴 HIGH (50-75%)**: Value = 0.9, peak demand
- **🟡 MEDIUM (75-100%)**: Value = 0.5, cooling down

AI agents become more aggressive during high stress periods to support the grid.

---

## 🛠️ Troubleshooting

### Dashboard won't start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
# 1. Make sure you're in the virtual environment
#    You should see (venv) in your terminal prompt
#    If not, activate it: source venv/bin/activate

# 2. Verify virtual environment is active
which python  # Should show path to venv/bin/python

# 3. Reinstall dependencies
pip install --upgrade pip
pip install -e .
```

**Common mistake:** Running commands outside the virtual environment. Always activate the venv first!

---

### Port already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Run on a different port
streamlit run thermal_commons_mvp/dashboard/app.py --server.port 8502
```

---

### Python version too old

**Error:** `requires-python = ">=3.10"`

**Solution:**
- Install Python 3.10 or higher from [python.org](https://www.python.org/downloads/)
- Create a new virtual environment with the correct version:
  ```bash
  # Remove old venv if it exists
  rm -rf venv
  
  # Create new venv with Python 3.10+
  python3.11 -m venv venv  # or python3.10, python3.12, etc.
  
  # Activate it
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  
  # Install dependencies
  pip install --upgrade pip
  pip install -e .
  ```

---

### Database errors

**Error:** SQLite database issues

**Solution:**
```bash
# Delete and recreate the database
rm data/cool_state.db
# Restart the dashboard
streamlit run thermal_commons_mvp/dashboard/app.py
```

---

### Map not loading

**Issue:** Map shows gray box or no buildings

**Solution:**
- Check internet connection (map tiles require internet)
- Try refreshing the browser (Ctrl/Cmd + Shift + R)
- The map uses WebGL; ensure your browser supports it

---

## 🔧 Advanced Configuration

### Customize Grid Stress Cycle

Edit `.env`:
```bash
# Change from 4 minutes to 10 minutes
GRID_CYCLE_MINUTES=10
```

### Change Dashboard Refresh Rate

Edit `.env`:
```bash
# Change from 3 seconds to 5 seconds
DASHBOARD_REFRESH_SECONDS=5
```

### Disable Database Persistence

Edit `.env`:
```bash
# Disable SQLite storage (trades/history won't persist)
ENABLE_PERSISTENCE=false
```

### Use Custom Database Path

Edit `.env`:
```bash
# Store database elsewhere
DB_PATH=/path/to/custom/cool_state.db
```

---

## 🧪 Running Tests (Optional)

To verify everything works correctly:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run only unit tests (faster)
pytest tests/unit/ -v
```

---

## 🌐 Optional: Run the API Backend

The dashboard works standalone, but you can also run the FastAPI backend separately:

```bash
# Terminal 1: Start API
uvicorn thermal_commons_mvp.api.main:app --reload

# Terminal 2: Start Dashboard
streamlit run thermal_commons_mvp/dashboard/app.py
```

API will be available at: `http://localhost:8000`  
Interactive docs at: `http://localhost:8000/docs`

---

## 📱 Accessing from Other Devices

To view the dashboard from another device on your network:

1. Find your computer's local IP address:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. Look for something like `192.168.1.X`

3. On the other device, navigate to:
   ```
   http://192.168.1.X:8501
   ```

---

## 🛑 Stopping the Dashboard

Press **Ctrl + C** in the terminal where the dashboard is running.

To deactivate the virtual environment:
```bash
deactivate
```

---

## 📚 Additional Resources

- **Technical README**: `README.md` - Developer documentation
- **Architecture**: `architecture.json` - System design
- **Dashboard Plan**: `DASHBOARD_AND_AGENTS_PLAN.md` - Feature specifications

---

## 🤝 Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review terminal output for error messages
3. Ensure all prerequisites are installed
4. Try restarting the dashboard

---

## 🎉 Success Checklist

- [ ] Python 3.10+ installed
- [ ] Repository cloned
- [ ] **Virtual environment created** (`python3 -m venv venv`)
- [ ] **Virtual environment activated** (see `(venv)` in prompt)
- [ ] **Dependencies installed** (`pip install -e .`)
- [ ] `.env` file created (`cp .env.example .env`)
- [ ] Dashboard launches without errors
- [ ] Browser opens to `http://localhost:8501`
- [ ] Map displays 50 buildings
- [ ] Simulation starts when clicking ▶️
- [ ] Trades appear in Agent Network
- [ ] Carbon counter increases

**Remember:** Always activate your virtual environment before running the dashboard!

**All checked?** You're ready to explore the COOL dashboard! 🚀

---

## 💡 Quick Tips

- **Best browser:** Chrome, Firefox, or Edge (Safari may have WebGL issues)
- **Performance:** Close unused browser tabs if the map is slow
- **Learning curve:** Spend 5 minutes clicking around to understand the UI
- **AI reasoning:** Hover over trade arrows to see why agents made decisions
- **Grid stress:** Watch how agent behavior changes as grid stress cycles

Enjoy exploring the future of decentralized energy trading! ⚡🏢
