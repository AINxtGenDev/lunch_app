#!/bin/bash

echo "=== Finding Conda Installation ==="
echo ""

echo "1. Your current shell:"
echo $SHELL
echo ""

echo "2. Which conda:"
which conda
echo ""

echo "3. Which python (in activated environment):"
which python
echo ""

echo "4. Which gunicorn (in activated environment):"
which gunicorn
echo ""

echo "5. Conda info:"
conda info --base
echo ""

echo "6. Current conda environment:"
echo $CONDA_DEFAULT_ENV
echo ""

echo "7. Conda environment prefix:"
echo $CONDA_PREFIX
echo ""

echo "8. List of conda environments:"
conda env list
echo ""

echo "9. Python path in current environment:"
python -c "import sys; print(sys.executable)"
echo ""

echo "10. Testing if gunicorn can import the app:"
python -c "from run import app; print('App imported successfully')"