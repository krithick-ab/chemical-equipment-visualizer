from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Dataset
from django.contrib.auth import get_user_model
from .serializers import DatasetSerializer
import pandas as pd
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from datetime import datetime
from django.core.files.base import ContentFile

class UploadCSVAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.dataset_set.count() >= user.csv_upload_limit:
            return Response({'error': f'You have reached your upload limit of {user.csv_upload_limit} CSV files.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_csv(file)
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_columns):
                return Response({'error': 'Missing required columns.'}, status=status.HTTP_400_BAD_REQUEST)

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            summary = {
                'total_count': len(df),
                'averages': df[numeric_cols].mean().to_dict(),
                'type_distribution': df['Type'].value_counts().to_dict(),
            }

            dataset = Dataset.objects.create(
                user=user,
                filename=file.name,
                summary=summary,
                csv_file=file
            )

            # Keep only the last 5 datasets
            # This logic needs to be updated to consider the user's limit
            # For now, I will remove it as the limit is handled above
            # old_datasets = Dataset.objects.order_by('-uploaded_at')[5:]
            # for old_dataset in old_datasets:
            #     old_dataset.delete()

            serializer = DatasetSerializer(dataset)
            response_data = serializer.data
            response_data['dataset_id'] = dataset.id  # Add this line
            response_data['equipment_data'] = df.to_dict(orient='records')

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        datasets = Dataset.objects.filter(user=request.user).order_by('-uploaded_at')
        
        # Manually construct the response data to include the filename
        response_data = []
        for dataset in datasets:
            response_data.append({
                'id': dataset.id,
                'filename': dataset.filename,
                'uploaded_at': dataset.uploaded_at,
                'summary': dataset.summary
            })
            
        return Response(response_data)


class DatasetDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dataset_id, *args, **kwargs):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
            serializer = DatasetSerializer(dataset)
            response_data = serializer.data

            # Read the CSV file and include its contents in the response
            if dataset.csv_file:
                df = pd.read_csv(dataset.csv_file.path)
                response_data['equipment_data'] = df.to_dict(orient='records')

            return Response(response_data)
        except Dataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND)

class DownloadPDFReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dataset_id=None):
        try:
            if dataset_id:
                if dataset_id == 'latest':
                    dataset = Dataset.objects.filter(user=request.user).latest('uploaded_at')
                else:
                    dataset = Dataset.objects.get(id=dataset_id, user=request.user)
            else:
                return Response({"error": "Dataset ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        except Dataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND)

        if not dataset.csv_file:
            return Response({"error": "CSV file not found for this dataset"}, status=status.HTTP_404_NOT_FOUND)

        df = pd.read_csv(dataset.csv_file.path)

        # Get chart parameters from request, with defaults
        bar_x = request.query_params.get('barX', 'Equipment Name')
        bar_y_str = request.query_params.get('barY', 'Flowrate,Pressure,Temperature')
        bar_y = bar_y_str.split(',')
        pie_data = request.query_params.get('pieData', 'Temperature')

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Chemical Equipment Parameter Report", styles['h1']))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Dataset ID: {dataset.id}", styles['Normal']))
        story.append(Paragraph(f"File Name: {dataset.filename}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Summary Stats
        summary = dataset.summary
        story.append(Paragraph(f"Total Equipment Count: {summary.get('total_count', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Average Flowrate: <b>{summary.get('averages', {}).get('Flowrate', 'N/A'):.2f}</b>", styles['Normal']))
        story.append(Paragraph(f"Average Pressure: <b>{summary.get('averages', {}).get('Pressure', 'N/A'):.2f}</b>", styles['Normal']))
        story.append(Paragraph(f"Average Temperature: <b>{summary.get('averages', {}).get('Temperature', 'N/A'):.2f}</b>", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Data Insights
        story.append(Paragraph("Data Insights", styles['h3']))
        story.append(Spacer(1, 0.1 * inch))
        insights = self.generate_data_insights(df)
        for insight in insights:
            story.append(Paragraph(insight, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Bar Chart
        story.append(Paragraph("Equipment Metrics", styles['h2']))
        bar_chart_img = self.create_bar_chart(df, bar_x, bar_y)
        story.append(Image(bar_chart_img, width=6 * inch, height=4 * inch))
        story.append(Spacer(1, 0.2 * inch))

        # Pie Chart
        story.append(Paragraph(f"{pie_data} Distribution", styles['h2']))
        pie_chart_img = self.create_pie_chart(df, pie_data)
        story.append(Image(pie_chart_img, width=4 * inch, height=3 * inch))
        story.append(Spacer(1, 0.2 * inch))

        # Data Table
        story.append(Paragraph("Raw Data", styles['h2']))
        data = [df.columns.values.tolist()] + df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#f7f7f7'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        story.append(table)

        doc.build(story)

        pdf_filename = f"report_{dataset.id}.pdf"
        buffer.seek(0)
        dataset.pdf_report.save(pdf_filename, ContentFile(buffer.read()), save=True)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        return response

    def generate_data_insights(self, df):
        insights = []
        insights.append(f"- This dataset contains data for {len(df)} pieces of equipment.")
        
        max_flowrate_eq = df.loc[df['Flowrate'].idxmax()]
        min_flowrate_eq = df.loc[df['Flowrate'].idxmin()]
        insights.append(f"- Flowrate ranges from {min_flowrate_eq['Flowrate']} to {max_flowrate_eq['Flowrate']}. Equipment with highest flowrate: {max_flowrate_eq['Equipment Name']}.")

        max_pressure_eq = df.loc[df['Pressure'].idxmax()]
        min_pressure_eq = df.loc[df['Pressure'].idxmin()]
        insights.append(f"- Pressure ranges from {min_pressure_eq['Pressure']} to {max_pressure_eq['Pressure']}. Equipment with highest pressure: {max_pressure_eq['Equipment Name']}.")

        max_temp_eq = df.loc[df['Temperature'].idxmax()]
        min_temp_eq = df.loc[df['Temperature'].idxmin()]
        insights.append(f"- Temperature ranges from {min_temp_eq['Temperature']} to {max_temp_eq['Temperature']}°C. Equipment with highest temperature: {max_temp_eq['Equipment Name']}.")

        return insights

    def get_category(self, df, col_name, value):
        if col_name == 'Temperature':
            if value < 290:
                return "Cool (<290°C)"
            elif 290 <= value < 310:
                return "Warm (290-310°C)"
            elif 310 <= value < 330:
                return "Moderately High (310-330°C)"
            elif 330 <= value < 350:
                return "High (330-350°C)"
            else:
                return "Extremely High (>350°C)"
        else:
            # For other numeric columns, create 4 equal-sized bins
            min_val = df[col_name].min()
            max_val = df[col_name].max()
            bin_width = (max_val - min_val) / 4
            
            if value < min_val + bin_width:
                return f"Low ({min_val:.2f} - {min_val + bin_width:.2f})"
            elif value < min_val + 2 * bin_width:
                return f"Medium-Low ({min_val + bin_width:.2f} - {min_val + 2 * bin_width:.2f})"
            elif value < min_val + 3 * bin_width:
                return f"Medium-High ({min_val + 2 * bin_width:.2f} - {min_val + 3 * bin_width:.2f})"
            else:
                return f"High ({min_val + 3 * bin_width:.2f} - {max_val:.2f})"

    def create_bar_chart(self, df, x_col, y_cols):
        fig, ax = plt.subplots(figsize=(10, 6))
        df.plot(x=x_col, y=y_cols, kind='bar', ax=ax)
        plt.title('Equipment Metrics')
        plt.ylabel('Values')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close(fig)
        img_buffer.seek(0)
        return img_buffer

    def create_pie_chart(self, df, data_col):
        df['category'] = df[data_col].apply(lambda x: self.get_category(df, data_col, x))
        distribution = df['category'].value_counts()
        
        fig, ax = plt.subplots()
        ax.pie(distribution, labels=distribution.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.title(f'{data_col} Distribution')

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close(fig)
        img_buffer.seek(0)
        return img_buffer