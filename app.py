from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import json
import uuid
from pipeline import Pipeline
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialize pipeline
pipeline = Pipeline()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.pdf'):
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        return jsonify({
            'session_id': session_id,
            'filename': filename,
            'message': 'File uploaded successfully'
        })
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

@app.route('/process', methods=['POST'])
def process_file():
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    # Find the uploaded file
    upload_dir = app.config['UPLOAD_FOLDER']
    files = [f for f in os.listdir(upload_dir) if f.startswith(session_id)]
    
    if not files:
        return jsonify({'error': 'File not found'}), 404
    
    filepath = os.path.join(upload_dir, files[0])
    
    try:
        # Process the file
        result = pipeline.run(filepath, save_json=False)
        
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            result = {'summary': 'Processing completed', 'raw_data': str(result)}
        
        # Save result for later download
        output_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_result.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'data': result,
            'session_id': session_id
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing file: {error_details}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/download/csv', methods=['GET'])
def download_csv():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    # Load result
    result_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_result.json")
    if not os.path.exists(result_file):
        return jsonify({'error': 'Result not found'}), 404
    
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    import pandas as pd
    from io import StringIO
    
    # Create CSV content
    output = StringIO()
    
    # Summary
    output.write("=== SUMMARY ===\n")
    output.write(f"{result.get('summary', 'N/A')}\n\n")
    
    # Entities
    if 'named_entities' in result and result['named_entities']:
        output.write("=== NAMED ENTITIES ===\n")
        try:
            df_entities = pd.DataFrame(result['named_entities'])
            df_entities.to_csv(output, index=False)
        except Exception:
            # Fallback if DataFrame creation fails
            for entity in result['named_entities']:
                output.write(f"{entity.get('text', 'N/A')},{entity.get('label', 'N/A')}\n")
        output.write("\n")
    
    # Tables
    if 'tables' in result:
        for i, table in enumerate(result['tables']):
            output.write(f"=== {table.get('title', f'Table {i+1}')} ===\n")
            if isinstance(table.get('data'), list) and len(table['data']) > 0:
                df_table = pd.DataFrame(table['data'])
                df_table.to_csv(output, index=False)
            output.write("\n")
    
    # Statistics
    if 'key_statistics' in result:
        output.write("=== KEY STATISTICS ===\n")
        df_stats = pd.DataFrame(result['key_statistics'])
        df_stats.to_csv(output, index=False)
        output.write("\n")
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'extracted_data_{session_id}.csv'
    )

@app.route('/download/pdf', methods=['GET'])
def download_pdf():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    # Load result
    result_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_result.json")
    if not os.path.exists(result_file):
        return jsonify({'error': 'Result not found'}), 404
    
    with open(result_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#283593'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph("Education Data Extraction Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                             styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    if result.get('summary'):
        elements.append(Paragraph("Summary", heading_style))
        elements.append(Paragraph(result['summary'], styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Document Type
    if result.get('document_type'):
        elements.append(Paragraph("Document Type", heading_style))
        elements.append(Paragraph(result['document_type'], styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Key Statistics
    if result.get('key_statistics'):
        elements.append(Paragraph("Key Statistics", heading_style))
        stats_data = [['Metric', 'Value', 'Context']]
        for stat in result['key_statistics']:
            stats_data.append([
                stat.get('metric', 'N/A'),
                stat.get('value', 'N/A'),
                stat.get('context', 'N/A')
            ])
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Policies and Schemes
    if result.get('policies_schemes'):
        elements.append(Paragraph("Policies & Schemes", heading_style))
        for policy in result['policies_schemes']:
            elements.append(Paragraph(f"<b>{policy.get('name', 'N/A')}</b>", styles['Normal']))
            elements.append(Paragraph(f"Description: {policy.get('description', 'N/A')}", styles['Normal']))
            elements.append(Paragraph(f"Target: {policy.get('target_audience', 'N/A')}", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        elements.append(Spacer(1, 0.2*inch))
    
    # Named Entities
    if result.get('named_entities'):
        elements.append(Paragraph("Named Entities", heading_style))
        entities_data = [['Entity', 'Type']]
        for entity in result['named_entities'][:50]:  # Limit to first 50
            entities_data.append([
                entity.get('text', 'N/A'),
                entity.get('label', 'N/A')
            ])
        entities_table = Table(entities_data, colWidths=[4*inch, 2*inch])
        entities_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(entities_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Tables
    if result.get('tables'):
        elements.append(PageBreak())
        elements.append(Paragraph("Extracted Tables", heading_style))
        for table in result['tables']:
            elements.append(Paragraph(f"<b>{table.get('title', 'Untitled Table')}</b>", styles['Heading3']))
            if isinstance(table.get('data'), list) and len(table['data']) > 0:
                # Convert table data to ReportLab table format
                table_data = []
                # Get headers from first row
                if table['data']:
                    headers = list(table['data'][0].keys())
                    table_data.append(headers)
                    for row in table['data']:
                        table_data.append([str(row.get(h, '')) for h in headers])
                    
                    pdf_table = Table(table_data)
                    pdf_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ]))
                    elements.append(pdf_table)
            elements.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'extracted_data_{session_id}.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

