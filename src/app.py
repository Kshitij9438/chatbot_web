from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app, resources={r"/chatbot": {"origins": "*"}})

# Model configuration
MODEL_NAME = "facebook/blenderbot-400M-distill"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto" if torch.cuda.is_available() else None,
    low_cpu_mem_usage=True
).eval()

# Simple in‑memory history
conversation_history = []
MAX_HISTORY = 4  # last 2 exchanges (user+bot)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/chatbot", methods=["POST"])
def handle_prompt():
    try:
        data = request.get_json()
        user_input = data.get("prompt", "").strip()
        if not user_input:
            return jsonify({"error": "Empty prompt"}), 400

        # Build context string from last exchanges
        history = " ".join(conversation_history[-MAX_HISTORY:])
        input_text = (history + " " + user_input).strip()

        # Tokenize + generate
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            pad_token_id=tokenizer.eos_token_id
        )
        bot_reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Update history and trim
        conversation_history.extend([user_input, bot_reply])
        conversation_history[:] = conversation_history[-MAX_HISTORY:]

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # debug=True auto‑reloads on code change
    app.run(host="0.0.0.0", port=5000, debug=True)
