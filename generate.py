import torch
import tiktoken
from src.model import RB, RBConfig

# Cargar modelo y pesos
checkpoint_path = "log/model_19072.pt"  # Cambia esto según el nombre de tu checkpoint
device = "cuda" if torch.cuda.is_available() else "cpu"

# Cargar el checkpoint
checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
config = checkpoint['config']
model = RB(config)
model.load_state_dict(checkpoint['model'])
model.to(device)
model.eval()

# Cargar el tokenizer
enc = tiktoken.get_encoding("gpt2")

def generate_text(prompt, max_length=30, top_k=60):
    """Genera texto autocompletando el prompt usando el modelo TinyRB"""
    tokens = enc.encode(prompt)
    tokens = torch.tensor(tokens, dtype=torch.long, device=device).unsqueeze(0)

    with torch.no_grad():
        for _ in range(max_length):
            logits, _ = model(tokens)
            logits = logits[:, -1, :]  # Última posición de la secuencia
            probs = torch.softmax(logits, dim=-1)
            topk_probs, topk_indices = torch.topk(probs, top_k)
            next_token = torch.multinomial(topk_probs, 1)  # Sampling top-k
            next_token = topk_indices.gather(-1, next_token)

            tokens = torch.cat((tokens, next_token), dim=1)
            if next_token.item() == enc.eot_token:  # Token de finalización
                break

    return enc.decode(tokens.squeeze(0).tolist())

# Modo interactivo en terminal
print("TinyRB model ready. Type a text and press ENTER to complete it (CTRL+C to exit).")
while True:
    try:
        user_input = input("\nPrompt: ")
        output = generate_text(user_input)
        print("\nTinyRB: " + output)
    except KeyboardInterrupt:
        print("\nExiting...")
        break
