import csv
from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(46, 204, 113) # Emerald Green
        self.cell(0, 10, 'Business Idea Novelty - System Accuracy Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(10)

def generate_pdf():
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Theoretical Accuracy Section
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, '1. Theoretical Accuracy (Mathematical Baseline)', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, "Based on the methodology established in 'TA-SBERT: Token Attention Sentence-BERT for Improving Sentence Representation' (Seo et al., 2022), semantic engines are evaluated using Semantic Textual Similarity (STS) tasks. The underlying SBERT architecture utilized in this system has been scientifically validated to achieve high Pearson and Spearman rank correlation coefficients against human-annotated gold labels. This confirms the mathematical validity of the engine's cosine similarity calculations.")
    pdf.ln(10)

    # 2. Practical Accuracy Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. Practical Accuracy (Live Golden Dataset Test)', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, "To evaluate the live web-scraping pipeline, a 'Golden Dataset' of 5 well-known business paradigms was processed through the live system. A True Positive (PASS) is recorded if the system successfully scrapes the live internet, semanticizes the data, and ranks the expected real-world competitor highly.")
    pdf.ln(5)

    # 3. Read CSV and Generate Table
    success_count = 0
    total = 0
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(85, 10, 'Test Idea (Abridged)', 1)
    pdf.cell(40, 10, 'Expected Target', 1)
    pdf.cell(30, 10, 'Match Score', 1)
    pdf.cell(30, 10, 'Status', 1, 1)
    
    pdf.set_font('Arial', '', 10)
    
    with open('accuracy_results.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if row['status'] == 'PASS':
                success_count += 1
            
            # Truncate idea for the table
            idea = row['idea'][:40] + "..." if len(row['idea']) > 40 else row['idea']
            
            pdf.cell(85, 10, idea, 1)
            pdf.cell(40, 10, row['expected'].title(), 1)
            pdf.cell(30, 10, f"{row['top_score']}%", 1)
            
            if row['status'] == 'PASS':
                pdf.set_text_color(46, 204, 113) # Green
            else:
                pdf.set_text_color(231, 76, 60) # Red
                
            pdf.cell(30, 10, row['status'], 1, 1)
            pdf.set_text_color(0, 0, 0) # Reset to black

    # 4. Final Score
    pdf.ln(10)
    accuracy = (success_count / total) * 100 if total > 0 else 0
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Final Live System Accuracy: {accuracy:.1f}%', 0, 1)

    pdf.output('Accuracy_Report.pdf')
    print("PDF Successfully Generated: Accuracy_Report.pdf")

if __name__ == "__main__":
    generate_pdf()