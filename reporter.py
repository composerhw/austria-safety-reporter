from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os
from html import escape
from config import OUTPUT_DIR, FILENAME_FORMAT, DATE_FORMAT

class PDFReporter:
    def __init__(self):
        self.font_path = "NanumGothic-Regular.ttf"
        self.font_name = "NanumGothic"
        
        # Register font
        if os.path.exists(self.font_path):
            pdfmetrics.registerFont(TTFont(self.font_name, self.font_path))
        else:
            print(f"Warning: Font file {self.font_path} not found. Korean characters may not display correctly.")

        # Create output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    def generate_report(self, news_items):
        date_str = datetime.now().strftime(DATE_FORMAT)
        filename = FILENAME_FORMAT.format(date=date_str) + ".pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='KoreanTitle', fontName=self.font_name, fontSize=18, leading=22, spaceAfter=20))
        styles.add(ParagraphStyle(name='KoreanHeading', fontName=self.font_name, fontSize=14, leading=18, spaceAfter=10))
        styles.add(ParagraphStyle(name='KoreanBody', fontName=self.font_name, fontSize=10, leading=14))
        styles.add(ParagraphStyle(name='KoreanLink', fontName=self.font_name, fontSize=9, leading=12, textColor=colors.blue))
        
        story = []
        
        # Title
        title_text = f"오스트리아 안전 뉴스 리포트 ({datetime.now().strftime('%Y-%m-%d')})"
        story.append(Paragraph(title_text, styles['KoreanTitle']))
        story.append(Spacer(1, 12))
        
        if not news_items:
            story.append(Paragraph("지난 24시간 동안 수집된 새로운 안전 관련 뉴스가 없습니다.", styles['KoreanBody']))
        else:
            story.append(Paragraph(f"총 {len(news_items)}건의 뉴스가 수집되었습니다.", styles['KoreanBody']))
            story.append(Spacer(1, 12))
            
            for i, item in enumerate(news_items, 1):
                # Item Title
                # Escape special characters to prevent XML parsing errors
                safe_title = escape(item['title_ko'])
                story.append(Paragraph(f"{i}. {safe_title}", styles['KoreanHeading']))
                
                # Original Title & Source
                safe_original = escape(item['original_title'])
                safe_source = escape(item['source'])
                meta_text = f"원문: {safe_original} | 출처: {safe_source} | {item['published'].strftime('%Y-%m-%d %H:%M')}"
                story.append(Paragraph(meta_text, styles['KoreanBody']))
                
                # Summary
                if item['summary_ko']:
                    safe_summary = escape(item['summary_ko'])
                    story.append(Paragraph(f"요약: {safe_summary}", styles['KoreanBody']))
                
                # Link
                # Escape URL for XML attribute (e.g. & -> &amp;)
                safe_link = escape(item['link'])
                link_text = f"<link href='{safe_link}'>기사 보러가기</link>"
                story.append(Paragraph(link_text, styles['KoreanLink']))
                
                story.append(Spacer(1, 20))
                
        # Build PDF
        try:
            doc.build(story)
            print(f"PDF Report generated: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None

    def generate_txt_report(self, news_items):
        date_str = datetime.now().strftime(DATE_FORMAT)
        filename = FILENAME_FORMAT.format(date=date_str) + ".txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"오스트리아 안전 뉴스 리포트 ({datetime.now().strftime('%Y-%m-%d')})\n")
                f.write("=" * 50 + "\n\n")
                
                if not news_items:
                    f.write("지난 24시간 동안 수집된 새로운 안전 관련 뉴스가 없습니다.\n")
                else:
                    f.write(f"총 {len(news_items)}건의 뉴스가 수집되었습니다.\n\n")
                    
                    for i, item in enumerate(news_items, 1):
                        f.write(f"{i}. {item['title_ko']}\n")
                        f.write(f"   원문: {item['original_title']}\n")
                        f.write(f"   출처: {item['source']} | {item['published'].strftime('%Y-%m-%d %H:%M')}\n")
                        if item['summary_ko']:
                            f.write(f"   요약: {item['summary_ko']}\n")
                        f.write(f"   링크: {item['link']}\n")
                        f.write("\n" + "-" * 30 + "\n\n")
            
            print(f"TXT Report generated: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error generating TXT: {e}")
            return None

if __name__ == "__main__":
    # Test
    reporter = PDFReporter()
    dummy_news = [{
        'title_ko': '테스트 뉴스 제목',
        'original_title': 'Test News Title',
        'source': 'Test Source',
        'published': datetime.now(),
        'summary_ko': '이것은 테스트 뉴스 요약입니다.',
        'link': 'http://google.com'
    }]
    reporter.generate_report(dummy_news)
