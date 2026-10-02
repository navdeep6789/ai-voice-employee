import re
from typing import List, Dict, Any
from pathlib import Path


class MarkdownChunker:
    """
    Splits markdown documents along logical section headers (H2/H3) and paragraphs
    to produce coherent chunks with metadata and source traceability.
    """

    @staticmethod
    def chunk_markdown(content: str, metadata: Dict[str, Any], max_chunk_words: int = 350) -> List[Dict[str, Any]]:
        # Extract title from H1 if present
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        doc_title = title_match.group(1).strip() if title_match else metadata.get("title", "Untitled Document")

        # Split on markdown section headers (## or ###)
        sections = re.split(r"\n(?=##+\s+)", content)
        chunks: List[Dict[str, Any]] = []
        chunk_idx = 0

        # Pre-process sections: if a section is very short (e.g. just H1 title), merge with next
        cleaned_sections = []
        pending_prefix = ""
        for sec in sections:
            sec_clean = sec.strip()
            if not sec_clean:
                continue
            if len(sec_clean.split()) < 15 and not sec_clean.startswith("##"):
                pending_prefix = (pending_prefix + "\n\n" + sec_clean).strip()
            else:
                if pending_prefix:
                    sec_clean = f"{pending_prefix}\n\n{sec_clean}"
                    pending_prefix = ""
                cleaned_sections.append(sec_clean)
        if pending_prefix:
            cleaned_sections.append(pending_prefix)

        for sec_clean in cleaned_sections:
            # Identify section heading
            sec_header_match = re.search(r"^(##+\s+.+)$", sec_clean, re.MULTILINE)
            sec_header = sec_header_match.group(1).strip() if sec_header_match else ""

            words = sec_clean.split()
            if len(words) <= max_chunk_words:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": sec_clean,
                    "metadata": {
                        **metadata,
                        "doc_title": doc_title,
                        "section_header": sec_header,
                        "word_count": len(words),
                    }
                })
                chunk_idx += 1
            else:
                # Sub-chunk by paragraphs with overlap
                paras = sec_clean.split("\n\n")
                curr_para_block: List[str] = []
                curr_words = 0

                for p in paras:
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    p_word_count = len(p_clean.split())
                    if curr_words + p_word_count > max_chunk_words and curr_para_block:
                        chunk_text = "\n\n".join(curr_para_block)
                        chunks.append({
                            "chunk_index": chunk_idx,
                            "content": chunk_text,
                            "metadata": {
                                **metadata,
                                "doc_title": doc_title,
                                "section_header": sec_header,
                                "word_count": curr_words,
                            }
                        })
                        chunk_idx += 1
                        # Retain last paragraph for sliding overlap
                        curr_para_block = [curr_para_block[-1], p_clean]
                        curr_words = len(curr_para_block[0].split()) + p_word_count
                    else:
                        curr_para_block.append(p_clean)
                        curr_words += p_word_count

                if curr_para_block:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": "\n\n".join(curr_para_block),
                        "metadata": {
                            **metadata,
                            "doc_title": doc_title,
                            "section_header": sec_header,
                            "word_count": curr_words,
                        }
                    })
                    chunk_idx += 1

        return chunks
