import os
import tempfile

from fastapi import FastAPI, HTTPException, UploadFile

from resume_parser import parse_resume

app = FastAPI(title="Resume Parser API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse")
def parse(file: UploadFile):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in (".pdf", ".docx", ".doc"):
        raise HTTPException(400, f"unsupported file type: {ext}")

    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(file.file.read())
    tmp.close()
    try:
        result = parse_resume(tmp.name)
    except ValueError as e:
        raise HTTPException(422, str(e))
    finally:
        os.unlink(tmp.name)

    result["source_file"] = file.filename
    return result
