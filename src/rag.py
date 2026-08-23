import re
from pathlib import Path
import yaml

KNOWLEDGE_BASE=Path(__file__).resolve().parent.parent/"knowledge-base"


def parse_document(file_path):
    text=file_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        metadata={}
        content=text
    else:
        parts=text.split("---",2)
        metadata=yaml.safe_load(parts[1]) or {}
        content=parts[2].strip()

    return metadata,content


def split_into_chunks(content):
    sections=re.split(r"\n(?=#+ )",content)

    chunks=[]

    for section in sections:
        section=section.strip()

        if not section:
            continue

        lines=section.splitlines()

        heading=lines[0].strip() if lines[0].startswith("#") else "General"

        body="\n".join(lines[1:]).strip()

        if body:
            chunks.append({
                "heading":heading,
                "content":body
            })

    return chunks


def load_knowledge_base():
    documents=[]

    for file_path in sorted(KNOWLEDGE_BASE.glob("*.md")):
        metadata,content=parse_document(file_path)
        chunks=split_into_chunks(content)

        for chunk in chunks:
            documents.append({
                "filename":file_path.name,
                "document_id":metadata.get("document_id"),
                "title":metadata.get("title"),
                "status":metadata.get("status"),
                "effective_date":str(metadata.get("effective_date","")),
                "last_reviewed":str(metadata.get("last_reviewed","")),
                "audience":metadata.get("audience"),
                "policy_authority":metadata.get("policy_authority"),
                "customer_answering":metadata.get("customer_answering",True),
                "heading":chunk["heading"],
                "content":chunk["content"]
            })

    return documents


def is_customer_source(document):
    if document["customer_answering"] is False:
        return False

    if document["status"] in ["superseded","draft"]:
        return False

    if document["audience"]!="customer":
        return False

    return True


def tokenize(text):
    stop_words={
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "do",
        "for",
        "from",
        "how",
        "i",
        "if",
        "in",
        "is",
        "it",
        "me",
        "my",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "was",
        "what",
        "when",
        "where",
        "which",
        "who",
        "with",
        "you",
        "aster",
        "row",
        "s"
    }

    words=re.findall(r"[a-z0-9]+",text.lower())

    return {
        word
        for word in words
        if word not in stop_words
    }

def search_knowledge_base(query,top_k=5):
    documents=load_knowledge_base()

    customer_documents=[
        document
        for document in documents
        if is_customer_source(document)
    ]

    query_words=tokenize(query)
    query_lower=query.lower()

    trailplus_query="trailplus" in query_lower or "trail plus" in query_lower
    standard_query="standard" in query_lower

    results=[]

    for document in customer_documents:
        heading_words=tokenize(document["heading"])
        content_words=tokenize(document["content"])

        if not query_words:
            continue

        heading_matches=query_words.intersection(heading_words)
        content_matches=query_words.intersection(content_words)

        score=0

        score+=len(heading_matches)*2
        score+=len(content_matches)

        if document["policy_authority"]=="official":
            score+=1

        if document["status"]=="active":
            score+=1

        document_text=(
        document["heading"]+" "+document["content"]
        ).lower()

        if trailplus_query:
            source_text=(
                document["filename"]+" "+
                str(document["title"])+" "+
                document["heading"]
            ).lower()

            if "trailplus" in source_text:
                score+=10
            elif "trailplus" in document_text:
                score+=3

        if standard_query and "standard" in document_text:
            score+=4

        match_count=len(
            heading_matches.union(content_matches)
        )

        if match_count==0:
            continue

        if match_count==1 and not heading_matches:
            continue

        document_copy=document.copy()
        document_copy["score"]=score
        document_copy["matched_words"]=sorted(
            heading_matches.union(content_matches)
        )

        results.append(document_copy)

    results.sort(
        key=lambda item:item["score"],
        reverse=True
    )

    return results[:top_k]
def format_source(document):
    return f"{document['filename']} — {document['heading']}"