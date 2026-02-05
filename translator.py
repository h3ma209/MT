import os
import time
from typing import List, Union
import ctranslate2
import transformers


class PolyglotTranslator:
    def __init__(
        self,
        model_name="facebook/nllb-200-distilled-1.3B",
        output_dir="nllb-1.3b-int8",
        device="auto",
    ):
        """
        Initialize the translator.

        Args:
            model_name: The HuggingFace model to use (default: NLLB-200 distilled 1.3B).
            output_dir: Where to store the converted CTranslate2 model.
            device: 'cpu', 'cuda', or 'auto'.
        """
        self.output_dir = output_dir
        self.model_name = model_name

        if device == "auto":
            self.device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        else:
            self.device = device

        print(f"Using device: {self.device}")

        # Ensure model is converted and available
        self._ensure_model()

        # Load Translator and Tokenizer
        print(f"Loading model logic from {self.output_dir}...")
        self.translator = ctranslate2.Translator(self.output_dir, device=self.device)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.model_name)

        # Language codes mapping for convenience
        self.lang_map = {
            "en": "eng_Latn",
            "english": "eng_Latn",
            "ar": "arb_Arab",
            "arabic": "arb_Arab",
            "ckb": "ckb_Arab",  # Sorani
            "sorani": "ckb_Arab",
            "kurdish_sorani": "ckb_Arab",
            "kmr": "kmr_Latn",  # Kurmanji
            "kurmanji": "kmr_Latn",
            "kurdish_kurmanji": "kmr_Latn",
        }

    def _ensure_model(self):
        """Check if CTranslate2 model exists, otherwise convert it."""
        if not os.path.exists(self.output_dir) or not os.listdir(self.output_dir):
            print(
                f"Model not found at {self.output_dir}. Converting {self.model_name}..."
            )
            print(
                "This requires downloading the 1.3B model (~2.5GB). It may take a few minutes."
            )

            try:
                converter = ctranslate2.converters.TransformersConverter(
                    self.model_name
                )
                converter.convert(self.output_dir, quantization="int8", force=True)
                print("Model conversion complete.")
            except Exception as e:
                print(f"Error during conversion: {e}")
                raise RuntimeError(
                    "Failed to convert model. Ensure dependencies are correct."
                )

    def detect_language(self, text: str) -> str:
        """
        Detect language using simple heuristics for the supported languages.
        Returns: 'en', 'ar', 'ckb', 'kmr'
        """
        # Arabic script chars range: 0x0600 - 0x06FF
        arabic_chars = set(c for c in text if "\u0600" <= c <= "\u06ff")

        if arabic_chars:
            # Distinguish between Arabic and Sorani (CKB)
            # Sorani specific/preferred chars
            sorani_markers = [
                "پ",
                "چ",
                "ژ",
                "گ",
                "ڤ",
                "ڕ",
                "ڵ",
                "ێ",
                "ۆ",
                "ە",
                "ک",
                "ی",
            ]
            # Arabic specific/preferred chars (Teh Marbuta, Tenween, etc)
            arabic_markers = ["ة", "ث", "ذ", "ض", "ظ", "ط", "ك", "ى", "ؤ", "إ", "أ"]

            sorani_score = sum(text.count(m) for m in sorani_markers)
            arabic_score = sum(text.count(m) for m in arabic_markers)

            # 'ک' and 'ی' are very common in Sorani, 'ك' and 'ي'/'ى' in Arabic
            # If scores are close, default to Arabic as it covers more standard cases unless explicit Sorani chars found
            if sorani_score > arabic_score:
                return "ckb"
            return "ar"

        else:
            # Latin script: Distinguish English vs Kurmanji
            # Kurmanji markers
            kmr_markers = ["ê", "î", "û", "ç", "ş", "Ê", "Î", "Û", "Ç", "Ş"]

            kmr_score = sum(text.count(m) for m in kmr_markers)
            if kmr_score > 0:
                return "kmr"
            return "en"

    def translate(
        self,
        text: Union[str, List[str]],
        source_lang: str = "auto",
        target_lang: str = "en",
    ) -> Union[str, List[str]]:
        """
        Translate text from source_lang to target_lang.

        Args:
            text: A string or list of strings to translate.
            source_lang: Source language code (e.g. 'en', 'ar', 'ckb', 'kmr') or 'auto'
            target_lang: Target language code.

        Returns:
            Translated text or list of texts.
        """
        is_single = isinstance(text, str)

        # Auto-detect source language if needed
        if source_lang == "auto":
            if is_single:
                source_lang = self.detect_language(text)
            else:
                # If list, detect for first element as approximation or handle individually?
                # For speed, detect on first element
                if text:
                    source_lang = self.detect_language(text[0])
                else:
                    source_lang = "en"  # Fallback

        if not source_lang:
            # Double check if source_lang ended up empty
            source_lang = "en"

        # Resolve language codes
        src_code = self.lang_map.get(source_lang.lower(), source_lang)
        tgt_code = self.lang_map.get(target_lang.lower(), target_lang)

        if is_single:
            text = [text]

        # Tokenize
        # NLLB requires source language to be set in tokenizer
        self.tokenizer.src_lang = src_code
        source = [
            self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(t)) for t in text
        ]

        # Translate
        # target_prefix needs to be the target language token
        target_prefix = [tgt_code]

        results = self.translator.translate_batch(
            source,
            target_prefix=[target_prefix] * len(source),
            beam_size=5,  # beam size
            num_hypotheses=1,
        )

        # Decode
        decoded_results = []
        for result in results:
            target = result.hypotheses[0]
            # Remove the target language token if it's the first token (it usually is)
            if target and target[0] == tgt_code:
                target = target[1:]

            decoded = self.tokenizer.decode(
                self.tokenizer.convert_tokens_to_ids(target)
            )
            decoded_results.append(decoded)

        if is_single:
            return decoded_results[0]
        return decoded_results


if __name__ == "__main__":
    try:
        # Initializing
        translator = PolyglotTranslator()

        print("\n--- Translator Ready ---")
        print(
            "Supported languages: English (en), Arabic (ar), Sorani (ckb), Kurmanji (kmr)"
        )

        sentences = [
            (
                "en",
                "ar",
                "I have been experiencing very slow internet speeds for the past three days.",
            ),
            (
                "ar",
                "en",
                "مشكلتي هي ان الرصيد يتم سحبه بشكل تلقائي وسريع جداً.",
            ),
        ]

        for src, tgt, txt in sentences:
            start = time.time()
            res = translator.translate(txt, src, tgt)
            end = time.time()
            print(f"[{src}->{tgt}] '{txt}' => '{res}' ({1000 * (end - start):.1f}ms)")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
