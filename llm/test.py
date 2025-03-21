# from transformers import AutoTokenizer, LlamaForCausalLM

# model = LlamaForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B")
# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")

# prompt = "Hey, are you conscious? Can you talk to me?"
# inputs = tokenizer(prompt, return_tensors="pt")

# # Generate
# generate_ids = model.generate(inputs.input_ids, max_length=30)
# tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

import transformers
import torch

model_id = "meta-llama/Meta-Llama-3.2-1B"

pipeline = transformers.pipeline("text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device_map="auto")
pipeline("Hey how are you doing today?")