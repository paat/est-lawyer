import sqlite3
import xml.etree.ElementTree as ET
import argparse
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_plain_text_from_xml(xml_string: str) -> str:
    """Extract plain text from XML document following Riigi Teataja structure."""
    if not xml_string or xml_string.strip() == '':
        return ''
    
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        logger.error(f"XML parsing error: {e}")
        return ''
    
    # Extract namespace from root tag
    namespace_match = re.match(r'\{.*\}', root.tag)
    namespace = namespace_match.group(0) if namespace_match else ''
    
    # Extract title
    title_elem = root.find(f'.//{namespace}aktinimi/{namespace}nimi/{namespace}pealkiri')
    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ''
    
    # Extract paragraphs
    paragraphs = []
    for paragrahv in root.findall(f'.//{namespace}sisu/{namespace}paragrahv'):
        # Get paragraph number
        kuvatav_nr_elem = paragrahv.find(f'{namespace}kuvatavNr')
        paragrahv_nr = kuvatav_nr_elem.text.strip() if kuvatav_nr_elem is not None and kuvatav_nr_elem.text else ''
        
        # Process clauses
        clause_texts = []
        for loige in paragrahv.findall(f'{namespace}loige'):
            sisu_tekst = loige.find(f'{namespace}sisuTekst')
            if sisu_tekst is not None:
                # Collect all text fragments
                texts = [text.strip() for text in sisu_tekst.itertext() if text.strip()]
                clause_text = ' '.join(texts)
                clause_texts.append(clause_text)
        
        # Combine paragraph number and clause texts
        paragraph_text = f"{paragrahv_nr} {' '.join(clause_texts)}".strip()
        if paragraph_text:
            paragraphs.append(paragraph_text)
    
    # Combine title and paragraphs
    plain_text = title
    if paragraphs:
        if plain_text:
            plain_text += '\n\n'
        plain_text += '\n\n'.join(paragraphs)
    
    return plain_text

def main():
    """Main function to process XML documents in database."""
    parser = argparse.ArgumentParser(description='Process XML documents in SQLite database')
    parser.add_argument('--db-path', required=True, help='Path to SQLite database file')
    args = parser.parse_args()
    
    try:
        conn = sqlite3.connect(args.db_path)
        cursor = conn.cursor()
        
        # Fetch documents with XML content
        cursor.execute("SELECT full_text_id, text_content_xml FROM legal_documents WHERE text_content_xml IS NOT NULL AND text_content_xml != ''")
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} documents to process")
        
        processed_count = 0
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for row in rows:
            full_text_id, xml_content = row
            plain_text = extract_plain_text_from_xml(xml_content)
            
            # Update database
            cursor.execute(
                "UPDATE legal_documents SET text_content_plain = ?, last_checked_at = ? WHERE full_text_id = ?",
                (plain_text, current_time, full_text_id)
            )
            processed_count += 1
            
            # Log progress every 10 documents
            if processed_count % 10 == 0:
                logger.info(f"Processed {processed_count}/{len(rows)} documents")
        
        conn.commit()
        logger.info(f"Successfully processed {processed_count} documents")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()