# Use a pipeline as a high-level helper
from transformers import pipeline

# # pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-1B")

# pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-1B", framework="pt", device=-1)
# result = pipe(
#     'this is a sample text: 2024 PVH Corp. Earnings Conference Call.    can you give me the year from this?  Just the single word'
# )
# print(result)



from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B")

# Define the input text (your HTML content or a prompt)
input_text = '''can you tell me something about me '''

# Tokenize the input text
inputs = tokenizer(input_text, return_tensors="pt")

# Generate a response from the model
output = model.generate(inputs['input_ids'], max_length=150, num_return_sequences=1)

# Decode the output
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

# Print the generated response
print(generated_text)
