import ctranslate2
translator = ctranslate2.Translator("nllb-1.3b-int8", device="cpu")
try:
    translator.translate_batch([["Hello", "world"]], repetition_penalty=1.2, no_repeat_ngram_size=3)
    print("Success")
except Exception as e:
    print(e)
