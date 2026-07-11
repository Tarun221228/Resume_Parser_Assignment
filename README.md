# Resume Parser API

Extracts contact info, education, work experience, skills, certifications
and projects from pdf / docx / doc resumes using OpenAI, returns JSON.

## Setup

```
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn main:app --reload
```

Or drop the key in a `.env` file instead of exporting it, it's loaded automatically.

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

## Tests

```
pytest tests.py -v
```

samples/ has a handful of intentionally messy resumes (generate them with
`python samples/generate_samples.py`) - a 2 page pdf with three jobs in
different date formats, a true two column pdf, a docx with contact info
and skills inside tables, a sidebar style pdf, and a docx where even the
work experience section is a table. Extraction and validation tests run
offline, the full end-to-end test runs only when OPENAI_API_KEY is set.
