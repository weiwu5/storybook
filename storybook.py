import io
from PIL import Image
import base64 
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr 

load_dotenv()

client = OpenAI()
messages=[
    {"role": "system", "content": "You are a writer to write stories for kids based on kid's input. Try to be short and finish every generation in 100 words."},
]

def get_completion(prompt):
    messages.append({"role": "user", "content": prompt})
    text_response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=messages,
      max_tokens=300,
    )
    story = text_response.choices[0].message.content
    messages.append({"role": "assistant", "content": story})

    response = client.images.generate(
        model="dall-e-3",
        prompt="draw a picture for this story: " + story,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    return story, base64_to_pil(response.data[0].b64_json)

def image_to_base64_str(pil_image):
    byte_arr = io.BytesIO()
    pil_image.save(byte_arr, format='PNG')
    byte_arr = byte_arr.getvalue()
    return str(base64.b64encode(byte_arr).decode('utf-8'))

def base64_to_pil(img_base64):
    base64_decoded = base64.b64decode(img_base64)
    byte_stream = io.BytesIO(base64_decoded)
    pil_image = Image.open(byte_stream)
    return pil_image

with gr.Blocks() as app:
    gr.Markdown("Story Books")
    with gr.Row():
        with gr.Column(scale=10):
            prompt = gr.Textbox(label="What story would you like to hear?", placeholder="Can you write a story about toothfairy?")
        with gr.Column(scale=1):    
            btn = gr.Button("What happen next?")
    
    with gr.Row():
        with gr.Column():
            story = gr.Textbox(label="Story", lines=15)
        with gr.Column():    
            output = gr.Image(label="Image")

    btn.click(fn=get_completion, inputs=[prompt], outputs=[story, output])

gr.close_all()
app.launch(share=True)