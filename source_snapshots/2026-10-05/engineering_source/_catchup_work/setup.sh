#!/usr/bin/env bash
# Creates ./venv next to this file from requirements.txt. Falls back to system python3 if pip can't install.
set -u
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
if "$PY" -m venv venv 2>/dev/null && venv/bin/pip install -q --upgrade pip >/dev/null 2>&1 && venv/bin/pip install -q -r requirements.txt; then
  echo "OK: venv ready -> $(pwd)/venv/bin/python ($(venv/bin/python --version))"
else
  echo "WARN: venv/pip install failed; falling back to system $PY. Needs: Pillow numpy opencv-contrib-python-headless (cairosvg, fonttools optional)."
  rm -rf venv; mkdir -p venv/bin; ln -sf "$(command -v "$PY")" venv/bin/python
  "$PY" -c "import PIL, numpy, cv2; print('system python has PIL', PIL.__version__, 'numpy', numpy.__version__, 'cv2', cv2.__version__)"
fi
