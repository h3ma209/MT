from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union
from translator import PolyglotTranslator
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Polyglot Translator API")

# Global translator instance
translator = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    global translator
    print("Initializing translator...")
    translator = PolyglotTranslator()


class TranslationRequest(BaseModel):
    text: Union[str, List[str]]
    source_lang: Optional[str] = "auto"
    target_lang: str = "en"


class TranslationResponse(BaseModel):
    translated_text: Union[str, List[str]]
    source_lang: str
    target_lang: str


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    if not translator:
        raise HTTPException(status_code=503, detail="Translator not initialized")

    try:
        # Handle empty source language or "auto"
        input_src = request.source_lang if request.source_lang else "auto"
        detected_src = input_src

        if input_src == "auto":
            # Detect language before translation
            if isinstance(request.text, str):
                detected_src = translator.detect_language(request.text)
            elif isinstance(request.text, list) and request.text:
                detected_src = translator.detect_language(request.text[0])
            else:
                detected_src = "en"  # Default fallback

        result = translator.translate(
            text=request.text, source_lang=detected_src, target_lang=request.target_lang
        )

        return TranslationResponse(
            translated_text=result,
            source_lang=detected_src,
            target_lang=request.target_lang,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
