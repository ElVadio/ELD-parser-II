import os
from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
import pdf2image
import pytesseract
import torch
import numpy as np
from PIL import Image

class DocumentProcessor:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.processor = LayoutLMv3Processor.from_pretrained(
            model_path or "microsoft/layoutlmv3-base"
        )
        self.model = LayoutLMv3ForTokenClassification.from_pretrained(
            model_path or "microsoft/layoutlmv3-base"
        ).to(self.device)

    def preprocess_pdf(self, pdf_path):
        """Convert PDF to images and extract text with layout."""
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            processed_pages = []

            for img in images:
                # Get OCR data
                ocr_data = pytesseract.image_to_data(
                    img, 
                    output_type=pytesseract.Output.DICT,
                    config='--psm 11'
                )

                # Process image for LayoutLM
                encoding = self.processor(
                    img,
                    return_tensors="pt",
                    truncation=True
                ).to(self.device)

                processed_pages.append({
                    'image': img,
                    'ocr_data': ocr_data,
                    'encoding': encoding
                })

            return processed_pages
        except Exception as e:
            raise Exception(f"PDF preprocessing failed: {str(e)}")

    def extract_fields(self, processed_page):
        """Extract specific fields from processed page."""
        try:
            # Get model predictions
            outputs = self.model(**processed_page['encoding'])
            predictions = outputs.logits.argmax(-1).squeeze().tolist()

            # Map predictions to OCR data
            ocr_data = processed_page['ocr_data']
            extracted_fields = {
                'timestamps': [],
                'events': [],
                'locations': [],
                'notes': []
            }

            for i, pred in enumerate(predictions):
                if i < len(ocr_data['text']):
                    text = ocr_data['text'][i]
                    conf = ocr_data['conf'][i]
                    
                    if conf > 60:  # Filter low confidence predictions
                        if pred == 1:  # Timestamp
                            extracted_fields['timestamps'].append(text)
                        elif pred == 2:  # Event
                            extracted_fields['events'].append(text)
                        elif pred == 3:  # Location
                            extracted_fields['locations'].append(text)
                        elif pred == 4:  # Note
                            extracted_fields['notes'].append(text)

            return extracted_fields
        except Exception as e:
            raise Exception(f"Field extraction failed: {str(e)}")

    def process_pdf(self, pdf_path):
        """Main processing pipeline."""
        try:
            processed_pages = self.preprocess_pdf(pdf_path)
            all_extracted_fields = []

            for page in processed_pages:
                fields = self.extract_fields(page)
                all_extracted_fields.append(fields)

            return self.post_process_results(all_extracted_fields)
        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")

    def post_process_results(self, extracted_fields):
        """Clean and structure extracted data."""
        return {
            'timestamps': self.clean_timestamps(
                [t for page in extracted_fields for t in page['timestamps']]
            ),
            'events': self.clean_events(
                [e for page in extracted_fields for e in page['events']]
            ),
            'locations': self.clean_locations(
                [l for page in extracted_fields for l in page['locations']]
            ),
            'notes': self.clean_notes(
                [n for page in extracted_fields for n in page['notes']]
            )
        }

    # Cleaning methods...