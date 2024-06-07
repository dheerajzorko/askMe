# askMe
# PDF Index Search with OpenAI GPT

## Overview

This Python program leverages the OpenAI GPT-3.5 model to assist in searching for specific sections within a PDF document based on user-provided questions. 
It extracts text from specified pages of the PDF, combines it with the questions, and queries GPT-3.5 to determine which section of the document might 
contain the answers to the questions.

## Features

- Extracts text from specified pages of a PDF document.
- Uses OpenAI GPT-3.5 to suggest which section(s) of the document might contain answers to user-provided questions.
- Outputs suggestions in JSON format, mapping each question to the suggested section(s) in the document.

## Dependencies

- Python 3.x
- `sys`
- `json`
- `fitz` (PyMuPDF)
- `openai` (OpenAI Python SDK)

## Installation

1. Install Python 3.x on your system if not already installed.
2. Install dependencies using pip:


pip install PyMuPDF openai

3. Obtain OpenAI API key and set it up as per OpenAI's instructions.

## Usage

Run the program from the command line using the following syntax:


python3 program.py <pdf_file> <questions_json>



- `<pdf_file>`: Path to the PDF document.
- `<questions_json>`: Path to a JSON file containing user-provided questions.

Example usage:

python3 askMe.py document.pdf questions.json


## How it Works

1. The program extracts text from the specified pages of the PDF document.
2. It combines each question from the provided JSON file with the extracted text to form a prompt.
3. The program sends this prompt to the OpenAI GPT-3.5 model.
4. GPT-3.5 suggests which section(s) of the document might contain answers to the questions.
5. The program outputs the suggestions in JSON format.

## Notes

- Ensure that the provided questions in the JSON file are relevant to the content of the PDF document.
- Adjust the `index_start_page` and `index_end_page` variables in the code to specify the range of pages from which text should be extracted for index 
search.

