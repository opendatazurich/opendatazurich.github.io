import requests
from huggingface_hub import InferenceClient
from google import genai
from openai import OpenAI
import pandas as pd
from pypdf import PdfReader



#### lese pdf

def download_document(doc_url, doc_filename):
    """Download and save a document.

    doc_url -- url of the document to download
    doc_filename -- name of the file that will be saved
    """
    print(f"lade {doc_url} herunter ...")
    # PDF herunterladen
    response = requests.get(doc_url)
    pdf_content = response.content

    # PDF speichern
    with open(doc_filename, 'wb') as f:
        f.write(pdf_content)

def read_pdf(doc_filename):
    """Read the contents of a pdf file.

    doc_filename -- filename or path of the pdf file
    """
    print(f"lese den Inhalt von {doc_filename} ...")
    # PDF auslesen
    reader = PdfReader(doc_filename)
    pdf_text = ''
    for page in reader.pages:
        pdf_text += page.extract_text()
    
    return pdf_text


#### hugging face teil
def connect_huggingface_client(hf_token):
    #model = "meta-llama/Meta-Llama-3-8B-Instruct"
    model = 'mistralai/Mistral-Nemo-Instruct-2407'
    model = 'mistralai/Mistral-7B-Instruct-v0.3'
    #model = 'google/gemma-2-2b-it' # ca 8000 tokens
    # model = 'Qwen/Qwen2.5-7B-Instruct'
    # model = 'microsoft/Phi-3-mini-4k-instruct' # ca 4000 tokens
    print("Starte Hugging Face InferenceClient Api Call mit Modell:", model)
    client = InferenceClient(model=model, token=hf_token)
    return client

def huggingface_inference_client_call(doc_text, client, doc_type):
    """API Call to hugging face to summarize a text.

    doc_text -- Text that will be summarized (e.g. content of pdf)
    hf_token -- Personal Hugging Face API Key
    """

    print("API Call Zusammenfassung")
    prompt_message = f"Fasse den Inhalt dieses Dokuments in einem Absatz auf deutsch zusammen und erwähne, dass es sich um ein {doc_type} handelt:" # Gib mir nur die Antwort:" # zweiter Satz braucht es bei llama
    messages = [{"role": "user", "content": f"{prompt_message} {doc_text}"}]
    client_output = client.chat_completion(messages, max_tokens=300)
    output_message = client_output.choices[0].message.content
    return output_message

def summarize_doc_pipeline(doc_url, doc_filename, client, doc_type):
    """Combine functions above to single pipeline."""
    download_document(doc_url, doc_filename)
    doc_text = read_pdf(doc_filename)
    return huggingface_inference_client_call(doc_text, client, doc_type)

def strip_text(doc_text, first_n_chars=None):
    """Strip input text because its too long"""
    # remove double blanks
    stripped_doc = doc_text.replace("\n \n","")
    stripped_doc = stripped_doc.replace("  "," ")

    # only use first n chars
    if first_n_chars:
        stripped_doc = stripped_doc[:first_n_chars]

    return stripped_doc

def connect_google_client(google_api_key):
    client = genai.Client(api_key=google_api_key)
    return client

def google_client_call(doc_url, doc_filename, client, doc_type):
    
    download_document(doc_url, doc_filename)

    model_id ='gemini-2.0-flash'

    uploaded_pdf = client.files.upload(file=doc_filename)
    print("Tokens:", client.models.count_tokens(model=model_id, contents=uploaded_pdf).total_tokens)

    prompt_message = f"Fasse den Inhalt dieses Dokuments in einem Absatz auf deutsch zusammen und erwähne, dass es sich um ein {doc_type} handelt:"

    response = client.models.generate_content(
    model=model_id,
    contents=[
        prompt_message,
        uploaded_pdf,
    ]
    )

    return response.text

def connect_openai_client(openai_api_key):
        client = OpenAI(api_key=openai_api_key)
        return client

def openai_client_call(doc_url, doc_filename, client, doc_type):
    download_document(doc_url, doc_filename)
    doc_text = read_pdf(doc_filename)

    prompt_message = f"Fasse den Inhalt dieses Dokuments in einem Absatz auf deutsch zusammen und erwähne, dass es sich um ein {doc_type} handelt:"

    model_id = "gpt-4o" #"gpt-3.5-turbo"
    # models = client.models.list()
    # for model in models:
    #     print(model.id)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt_message} {doc_text}",
            }
        ],
        model=model_id,
    )
    return chat_completion.choices[0].message.content

if __name__ == "__main__":

    hf_token = 'XXXX'
    doc_url = 'https://amsquery.stadt-zuerich.ch/Dateien/0/D29.pdf'
    doc_filename = 'pdf_download.pdf'
    client = connect_huggingface_client(hf_token)
    output_message = summarize_doc_pipeline(doc_url, doc_filename, client)
    print(output_message)