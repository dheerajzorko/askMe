import traceback
import gc
import sys
import json
import fitz
from openai import OpenAI

def extract_page_content(pdf_file,index_start_page,index_end_page):
    text = ""
    doc =  fitz.open(pdf_file)
    for page in doc[index_start_page-1:index_end_page]:
        text += page.get_text()
    del page
    gc.collect()
    doc.close()
    return text

def get_pages_stats():
    document = fitz.open(pdf_file)
    num_pages = document.page_count
    gc.collect()
    document.close()
    return num_pages

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

def find_individual_pages(index_text,answer_dict):
    pages = {}
    for i in answer_dict.keys():
        #print(i)    #   questions
        #print(answer_dict[i])   #content_page reference
        if answer_dict[i] != '':
            content_system_prompt = '''
            X is the context page in a pdf file with pages numbers next to it,
                find the start and end page number for Y

            Y is the context page heading

                Don't give explanation, only output, heading, its start page and end page.

                use the following JSON format
                {
                    heading:{
                    start_page:start_page_value,
                    end_page:end_page_value,
                    }

                }
            '''
            content_user_prompt = f'''
            X:"{index_text}"
            Y:"{i}"

            '''
            s_e_pages = query_gpt(content_system_prompt,content_user_prompt)
            pages.update(json.loads(s_e_pages))
        else:   
            pass
    return pages

def manualScan(pdf_file,question,index_end_page):

    total_pages = get_pages_stats()+1
    for i in range(index_end_page+1,total_pages):
        #print("page:",i)
        manual_scan_context = extract_page_content(pdf_file,i,i)
        #print(manual_scan_context)
        #print("page",i,"end")
        manual_question_system_prompt = '''search the following DOcument and answer the following questions, don't give explanation. if you cant find the answer, respond with "" '''
        manual_question_user_prompt = f"DOcument: {manual_scan_context}\n\nQuestion: {question}"

        manual_answer = query_gpt(manual_question_system_prompt,manual_question_user_prompt)

        if manual_answer != "":
            return manual_answer

    return "Data Not Available"

def load_questions_sections(questions,index_text):
    questions_and_context_sections = ""
    sections_from_gpt_search = ""
    for question_obj in questions:
        question = questions[question_obj]
        index_system_prompt = '''take the input string as index document and output the section should i check to find more details about the following questions with page . only say the section name, dont add prefix or suffix or explain or add additional formatting. output should be in JSON format {[question:refrrence]} if you cannot find the reference, keep the output empty for that question'''
        index_user_prompt = f"DOcument: {index_text}\n\nQuestion: {question}"
        sections_from_gpt_search += query_gpt(index_system_prompt,index_user_prompt)
    questions_and_context_sections = sections_from_gpt_search
    return questions_and_context_sections



def process_questions(pdf_file, questions_json, index_start_page, index_end_page):
    with open(questions_json, 'r') as f:
        questions = json.load(f)

    #print(questions)

    index_text = extract_page_content(pdf_file,index_start_page,index_end_page)

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
        #print(f"Answer: {answer}")
        answer_dict = json.loads(answer)
        response = find_individual_pages(index_text,answer_dict)
        #print(response)
        output = {}
        #print(answer_dict)
        for j in answer_dict.keys():
            #print(j,answer_dict[j])
            if answer_dict[j] == "":
                output[j]=manualScan(pdf_file,j,index_end_page)
                #print(output)
            else:
                selected_page_start = response[j]["start_page"]
                selected_page_end = response[j]["end_page"]
                #print(selected_page_start,selected_page_end)
                selective_context = extract_page_content(pdf_file,selected_page_start,selected_page_end)

                selected_system_prompt = '''search the following DOcument and answer the following questions,
don't give explanation'''

                selected_user_prompt = f"DOcument: {selective_context}\n\nQuestion: {j}"

                selected_answer = query_gpt(selected_system_prompt,selected_user_prompt)
                output[j]=selected_answer

        #print(output)
    return output

def load_questions_to_json(questions_json):
    with open(questions_json, 'r') as f:
        questions = json.load(f)
    return questions

def answer_questions_with_page_sections(questions_and_context_sections_dict,questions_and_pages_dict):
    output = {}

    #print(answer_dict)
    for j in questions_and_context_sections_dict.keys():
        #print(j,answer_dict[j])
        if questions_and_context_sections_dict[j] == "":
            output[j]=manualScan(pdf_file,j,index_end_page)
            #print(output)
        else:
            selected_page_start = questions_and_pages_dict[j]["start_page"]
            selected_page_end = questions_and_pages_dict[j]["end_page"]
            #print(selected_page_start,selected_page_end)
            selective_context = extract_page_content(pdf_file,selected_page_start,selected_page_end)
            selected_system_prompt = '''search the following DOcument and answer the following questions, don't give explanation'''
            selected_user_prompt = f"DOcument: {selective_context}\n\nQuestion: {j}"

            selected_answer = query_gpt(selected_system_prompt,selected_user_prompt)
            output[j]=selected_answer

    return output


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: python program.py <pdf_file> <questions_json>")
    #     sys.exit(1)

    context_page_headings = ["content","context",""]

    #read context page and respective sections
        #find start and eng page of context page

    questions = {}
    pdf_file = sys.argv[1]
    questions_json = sys.argv[2]
    index_start_page = 2
    index_end_page = 3

    #select questions and find their respective sections
    try:
        questions = load_questions_to_json(questions_json)
        #print(questions)
        index_text = extract_page_content(pdf_file,index_start_page,index_end_page)
        #print(index_text)
        questions_and_context_sections = load_questions_sections(questions,index_text)
        questions_and_context_sections_dict = json.loads(questions_and_context_sections)
        #if section found:
            #for each quetion's respective section, find the section's start and end page
        questions_and_pages_dict = find_individual_pages(index_text,questions_and_context_sections_dict)
            #start answering questions acc to page ranges

        print(answer_questions_with_page_sections(questions_and_context_sections_dict,questions_and_pages_dict))


        #if section not found:
            #load each page and find answers to set of quetions until answer if found
            #if answer is not yet found after scanning the whole document, say "Data Not Available"
        
    except Exception as e:        
        print("Cannot Answer Questions!")
        traceback.print_exc()

    # pdf_file = sys.argv[1]
    # questions_json = sys.argv[2]
    # index_start_page = 2
    # index_end_page = 3
    #print(process_questions(pdf_file,questions_json,index_start_page,index_end_page))
