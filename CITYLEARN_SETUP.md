# CityLearn Integration Guide

> **⚠️ Status: Shelved**  
> CityLearn integration has been **shelved** for this project due to installation and dependency compatibility issues. The dashboard currently uses **mock telemetry** (random values) which works reliably.

## Overview

The dashboard currently uses **mock telemetry** (random values) for simulation. This guide documents how **CityLearn** (or similar information sources) can be integrated in the future to provide scientifically-valid building energy models based on real building physics and real-world conditions.

**Note:** Information sources like CityLearn can be included in the project to reflect real-world conditions, but are not required for the core functionality.

## Why CityLearn Was Shelved

CityLearn installation encountered persistent issues:
- **Cython compilation errors** with scikit-learn 1.0.2 on Python 3.11
- **Dependency conflicts** with newer Python versions (3.14+)
- **Network/DNS issues** during installation attempts
- **Build failures** even with pre-built wheels and Cython downgrades

The project works perfectly with mock telemetry, so CityLearn integration was shelved to focus on core functionality.

## Future Integration

If you want to integrate CityLearn or similar real-world data sources in the future, follow the steps below. The codebase is already structured to support this - the simulation engine will automatically detect and use CityLearn if available.

## Prerequisites

- Python 3.10+ (3.11 recommended)
- Virtual environment (recommended - CityLearn has dependency conflicts)
- Stable internet connection

## Step 1: Install CityLearn

**Important:** 
- The PyPI package name is **`CityLearn`** (capital C and L), not `citylearn`
- CityLearn pins older versions of `gymnasium` and `pandas`. The README recommends using a **separate virtualenv** for CityLearn to avoid conflicts.
- **Network required:** You need internet access to install from PyPI

### Option A: Separate Virtualenv (Recommended)

**Important:** CityLearn works best with Python 3.10 or 3.11. Python 3.14 may have compatibility issues.

```bash
# Create a new virtualenv for CityLearn (use Python 3.10 or 3.11 if available)
python3.11 -m venv venv-citylearn  # Or python3.10
source venv-citylearn/bin/activate  # On Windows: venv-citylearn\Scripts\activate

# Upgrade pip, setuptools, wheel first (fixes build issues)
pip install --upgrade pip setuptools wheel

# Install CityLearn (note: package name is "CityLearn" with capital C and L)
# Try with --only-binary first to avoid Cython compilation issues
pip install --only-binary :all: CityLearn

# If that fails, try installing compatible Cython first, then CityLearn
# pip install "Cython<3.0"
# pip install CityLearn

# Install the project with simulation extras
cd "/Users/chinmunyau/Coding Stuff/DataDoms HFC"
pip install -e ".[simulation]"
```

**If you only have Python 3.14:**
- CityLearn may fail to install due to old dependencies (pandas 1.3.5 doesn't build on 3.14)
- Consider using Python 3.11 or 3.10 for the CityLearn venv
- Or wait for CityLearn to update their dependencies

### Option B: Same Virtualenv (May Have Conflicts)

```bash
# In your existing venv
pip install CityLearn
pip install -e ".[simulation]"
```

**Note:** If you get dependency conflicts (e.g., gymnasium version), use Option A.

## Step 2: Get CityLearn Schema/Data

CityLearn needs a **schema file** (JSON) that defines the building environment. You have three options:

### Option A: Use CityLearn's Built-in Dataset (Easiest)

The code will automatically use CityLearn's tropical dataset if no schema path is provided. This works out of the box:

```bash
# No .env changes needed - code uses placeholder
```

### Option B: Download CityLearn Challenge Dataset

1. Visit: https://www.citylearn.net/
2. Download a dataset (e.g., "citylearn_challenge_2020_climate_zone_1")
3. Extract it to a directory, e.g., `~/citylearn_data/`
4. Find the `schema.json` file in that directory

### Option C: Use Your Own Schema

If you have a custom CityLearn schema, point to it in `.env`:

```bash
CITYLEARN_SCHEMA_PATH=/path/to/your/schema.json
```

## Step 3: Configure Environment

Edit `.env`:

```bash
# CityLearn / Simulation
CITYLEARN_SCHEMA_PATH=/path/to/schema.json  # Optional - leave empty for built-in dataset
CITYLEARN_BUILDING_ID=Building_5  # Building ID in CityLearn schema
```

**If `CITYLEARN_SCHEMA_PATH` is empty**, the code will use CityLearn's built-in tropical dataset.

## Step 4: Test CityLearn Integration

Test that CityLearn works:

```bash
# Run the CityLearn gym test
python -m thermal_commons_mvp.simulation.city_gym

# Or use the convenience command
cool-sim
```

You should see output like:
```
reset -> temp=24.5, humidity=60.0, power_load=52.3
step  -> temp=24.6, humidity=59.8, power_load=51.9
step  -> temp=24.7, humidity=60.1, power_load=53.2
```

If you see warnings like "CityLearn not installed", go back to Step 1.

## Step 5: Enable CityLearn in Dashboard

The code has been updated to automatically use CityLearn if available. The dashboard will:

1. **Check if CityLearn is installed** - if not, falls back to mock data
2. **Use CityLearnGym** to generate realistic telemetry
3. **Apply to all 50 buildings** - currently uses one CityLearn instance for all (see "Architecture Notes" below)

## Step 6: Run Dashboard

```bash
# Make sure you're in the CityLearn venv (if using separate venv)
source venv-citylearn/bin/activate

# Run dashboard
streamlit run thermal_commons_mvp/dashboard/app.py
```

The dashboard should now use CityLearn for telemetry instead of random values.

## Architecture Notes

### Current Implementation

The code uses **one CityLearnGym instance** for all 50 buildings. This means:
- All buildings share the same energy dynamics
- Each building gets slightly different values due to step offsets
- This is simpler and less resource-intensive

### Future Enhancement (Optional)

To have **unique dynamics per building**, you could:
1. Create 50 separate CityLearnGym instances (one per building)
2. Use a multi-building CityLearn schema
3. Map each building to a different building in the CityLearn dataset

This requires more memory and setup but provides more realistic diversity.

## Troubleshooting

### Python version too new (3.14+)

**Error:** `BackendUnavailable: Cannot import 'setuptools.build_meta'` or pandas/scikit-learn build failures

**Solution:** CityLearn requires older dependencies that may not build on Python 3.14. Use Python 3.10 or 3.11:

```bash
# Check available Python versions
python3.11 --version  # or python3.10
# If available, recreate venv with older Python:
deactivate
rm -rf venv-citylearn
python3.11 -m venv venv-citylearn
source venv-citylearn/bin/activate
pip install --upgrade pip setuptools wheel
pip install CityLearn
```

### Network/DNS errors when installing

**Error:** `Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known`

**Solutions:**
1. **Check internet connection** - Make sure you're connected to the internet
2. **Check DNS** - Try: `ping pypi.org` to see if DNS resolution works
3. **Use proxy if needed:**
   ```bash
   pip install --proxy http://your-proxy:port CityLearn
   ```
4. **Install from GitHub (if PyPI is blocked):**
   ```bash
   pip install git+https://github.com/intelligent-environments-lab/CityLearn.git
   ```

### "CityLearn not installed" warning

**Solution:** Install CityLearn (Step 1). Make sure you use the correct package name: **`CityLearn`** (capital C and L), not `Citylearn` or `citylearn`

### Cython compilation errors (scikit-learn build failure)

**Error:** `Cython.Compiler.Errors.CompileError: sklearn/ensemble/_hist_gradient_boosting/splitting.pyx` or `Cannot assign type ... except? -1 nogil' to '... noexcept nogil'`

**Cause:** scikit-learn 1.0.2 (required by CityLearn) fails to compile with newer Cython versions on Python 3.11.

**Solutions:**

**Option 1: Use pre-built wheels (recommended)**
```bash
# Force pip to use binary wheels, don't build from source
pip install --only-binary :all: CityLearn
```

**Option 2: Downgrade Cython before installing**
```bash
# Install compatible Cython version first
pip install "Cython<3.0"
# Then install CityLearn
pip install CityLearn
```

**Option 3: Install dependencies manually with compatible versions**
```bash
# Install compatible versions first
pip install "numpy<1.24" "pandas==1.3.5" "scikit-learn==1.0.2" "gymnasium<=0.28.1" "Cython<3.0"
# Then install CityLearn (it should use the pre-installed deps)
pip install CityLearn
```

**Option 4: Use conda (if available)**
```bash
conda install -c conda-forge citylearn
```

### Setuptools/build errors

**Error:** `Cannot import 'setuptools.build_meta'` or build failures

**Solutions:**
1. Upgrade build tools:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```
2. Use Python 3.10 or 3.11 (not 3.14+)
3. If using Python 3.14, you may need to wait for CityLearn to update dependencies

### "No CityLearn schema path; using placeholder"

**Solution:** This is OK! The code will use CityLearn's built-in dataset. If you want a custom schema, set `CITYLEARN_SCHEMA_PATH` in `.env`.

### Dependency conflicts (gymnasium, pandas)

**Solution:** Use a separate virtualenv (Option A in Step 1)

### Import errors

**Solution:** Make sure you're in the correct virtualenv and have run `pip install -e ".[simulation]"`

## Verification

To verify CityLearn is working:

1. **Check logs** - should see "CityLearn environment initialized" (not "CityLearn not installed")
2. **Check telemetry** - values should be realistic (not pure random)
3. **Check time series** - should show realistic building dynamics over time

## Current Status

**CityLearn integration is shelved.** The dashboard works with mock telemetry. If you need real-world building energy data in the future, you can:

1. Follow this guide to attempt CityLearn installation
2. Use alternative data sources (e.g., real BMS data via BACnet)
3. Integrate other simulation libraries that provide building energy models

The codebase is structured to support these integrations - the simulation engine will automatically detect and use available data sources.
- Consider multi-building schemas for more diversity
