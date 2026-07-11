# Resume Parser API

Extracts contact info, education, work experience, skills, certifications
and projects from pdf / docx / doc resumes using OpenAI, returns JSON.

## Setup

```
uv sync
uvicorn main:app --reload
```

Set OPENAI_API_KEY in a `.env` file, it's loaded automatically.

Open http://localhost:8000/docs and upload a resume on the /parse endpoint.

Or from the command line:

```
python resume_parser.py samples/complex_resume.pdf
```

For old .doc files, libreoffice needs to be installed for conversion.

## How it works

1. Text is extracted based on file type - pymupdf for pdf, python-docx
   for docx (tables included, resumes often keep contact info there),
   libreoffice conversion for old .doc files.
2. The text goes to gpt-4o with a fixed JSON format in the prompt,
   response_format=json_object, temperature 0. The prompt also asks it to
   reason step by step through each section first (contact, education,
   every job, skills, certifications/projects) before filling in the
   JSON, since resumes list jobs in all sorts of date formats and that
   scratch space helps it not skip one. The reasoning itself gets
   stripped out before returning the result, it's not part of the
   output.
3. Since LLMs sometimes make values up, the result is checked back
   against the resume text - email and phone must actually appear in it
   (phone compared digits-only), company names, certifications and
   project names are checked too. Anything suspicious is dropped or
   listed in "warnings".

I used an LLM instead of a BERT NER model because NER gives loose tokens
that need a lot of post-processing to turn into structured records, while
an LLM handles the layout differences between resumes and gives the target
JSON directly. Step 3 covers the hallucination risk that comes with that.

samples/ has a few sample resumes to try it on, including a two column
layout and a sidebar style layout.
