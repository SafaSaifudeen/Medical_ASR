from flask import Flask, request, jsonify
import os
import torch
import torchaudio
from transformers import (
    Wav2Vec2Processor, Wav2Vec2ForCTC,
    AutoTokenizer, AutoModelForSeq2SeqLM
)
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================
# Model Loaders
# ============================
def load_asr_model(model_path="../ml/models/wav2vec2-finetuned-final"):
    processor = Wav2Vec2Processor.from_pretrained(model_path)
    model = Wav2Vec2ForCTC.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return processor, model, device

def load_llm_model(model_path="../ml/models/my_finetuned_medical_model"):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return tokenizer, model, device

asr_processor, asr_model, asr_device = load_asr_model()
llm_tokenizer, llm_model, llm_device = load_llm_model()

# ============================
# Helper Functions
# ============================
def process_audio_file(file_bytes, target_sample_rate=16000):
    with open("temp_audio.wav", "wb") as f:
        f.write(file_bytes)
    signal, sample_rate = torchaudio.load("temp_audio.wav")
    os.remove("temp_audio.wav")

    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        signal = resampler(signal)
        sample_rate = target_sample_rate
    return signal, sample_rate

def asr_predict(signal, sample_rate):
    input_values = asr_processor(signal.squeeze().numpy(), sampling_rate=sample_rate, return_tensors="pt").input_values
    input_values = input_values.to(asr_device)
    with torch.no_grad():
        logits = asr_model(input_values).logits
    pred_ids = torch.argmax(logits, dim=-1)
    transcript = asr_processor.batch_decode(pred_ids)[0]
    return transcript

def llm_predict(transcript):
    prompt = "Correct: " + transcript.lower()
    inputs = llm_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
    inputs = {k: v.to(llm_device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = llm_model.generate(inputs["input_ids"], max_length=256)
    response = llm_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def compute_bleu_score(reference, hypothesis):
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()
    smoothie = SmoothingFunction().method1
    score = sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=smoothie)
    return score

# ============================
# API Routes
# ============================
@app.route("/transcribe", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    actual_transcription = request.form.get("reference")

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        file_bytes = file.read()
        signal, sample_rate = process_audio_file(file_bytes)
        asr_transcript = asr_predict(signal, sample_rate)
        llm_response = llm_predict(asr_transcript)

        result = {
            "asr_transcript": asr_transcript,
            "llm_response": llm_response,
            "transcription": llm_response
        }

        if actual_transcription:
            result["bleu_asr"] = compute_bleu_score(actual_transcription, asr_transcript)
            result["bleu_llm"] = compute_bleu_score(actual_transcription, llm_response)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================
# Run Flask App
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)