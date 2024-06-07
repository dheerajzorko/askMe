import sys
import json
import fitz
from openai import OpenAI

def extract_index_page(pdf_file,index_start_page,index_end_page):
    text = ""
    with fitz.open(pdf_file) as doc:
        for page in doc[index_start_page-1:index_end_page]:
            text += page.get_text()
    return text

def open_specific_page(pdf_file,index):
    text = ""
    with fitz.open(pdf_file) as doc:
        for page in doc[index_start_page-1:index_end_page]:
            text += page.get_text()
    return text    
    

def query_gpt(system,user):
    """
    Send prompt to GPT for processing and retrieve the generated answer.
    """
    client = OpenAI()
    
    try:
        completion = client.chat.completions.create(
          model="gpt-3.5-turbo-0125",
          messages=[
            {"role": "system", "content": system },
            {"role": "user", "content": user }
          ]
        )
        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error processing prompt: {e}")
        return "Data Not Available"

def find_individual_answer(answer):
    return

def process_questions(pdf_file, questions_json, index_start_page, index_end_page):
    with open(questions_json, 'r') as f:
        questions = json.load(f)

    #print(questions)

    index_text = extract_index_page(pdf_file,index_start_page,index_end_page)

    for question_obj in questions:
        question = questions[question_obj]
        # Combine question with index text
        index_system_prompt = '''take the input string as index document and output the section should i check to find more details about the following questions with page .
only say the section name, dont add prefix or suffix or explain or add additional formatting.
output should be in JSON format
{[question:refrrence]}
if you cannot find the reference, keep the output empty for that question'''

        #index_system_prompt = "take the input string as index document and tell me which section should i check to find more details about the following questions with page"
        index_user_prompt = f"DOcument: {index_text}\n\nQuestion: {question}"
        # Query GPT for an answes
        answer = query_gpt(index_system_prompt,index_user_prompt)
        #print(f"Question: {question}")
        #print(f"prompt: {prompt}")
        print(f"Answer: {answer}")
        #response = find_individual_answer(answer)        
        #print(response)
    return


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python program.py <pdf_file> <questions_json>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    questions_json = sys.argv[2]
    index_start_page = 2
    index_end_page = 3
    process_questions(pdf_file,questions_json,index_start_page,index_end_page)
