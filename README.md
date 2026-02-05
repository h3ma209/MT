# Rayeid Translator

A lightweight, fast, offline neural machine translator supporting **English**, **Arabic**, and **Kurdish (Sorani & Kurmanji)**.

Powered by [CTranslate2](https://github.com/OpenNMT/CTranslate2) and a solidified/quantized version of [NLLB-200](https://huggingface.co/facebook/nllb-200-distilled-600M).

## Features

- **Fast Inference**: Uses CTranslate2 with INT8 quantization.
- **Lightweight**: Optimized model size (~600MB).
- **Offline Capable**: Once the model is converted on the first run, no internet is required.
- **Languages**: 
  - English (`en`)
  - Arabic (`ar`)
  - Kurdish Sorani (`ckb`)
  - Kurdish Kurmanji (`kmr`)

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **First Run Setup**:
   The first time you run the script, it will automatically download the `facebook/nllb-200-distilled-600M` model and convert it to the optimized CTranslate2 format. This requires an internet connection and takes about a minute.

## Usage

### Command Line
You can run the script directly to see a demo:
```bash
python3 translator.py
```

### Python API
```python
from translator import PolyglotTranslator

# Initialize (will load optimized model)
translator = PolyglotTranslator()

# Translate
# English to Sorani
print(translator.translate("Hello friend", source_lang="en", target_lang="ckb"))

# Arabic to Kurmanji
print(translator.translate("مرحبا", source_lang="ar", target_lang="kmr"))
```
