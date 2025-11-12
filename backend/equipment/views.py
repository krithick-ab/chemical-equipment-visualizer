from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Dataset
from .serializers import DatasetSerializer
import pandas as pd
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from datetime import datetime
from django.core.files.base import ContentFile

class UploadCSVAPIView(APIView):
    def post(self, request, *args, **kwargs):
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
                filename=file.name,
                summary=summary,
                csv_file=file
            )

            # Keep only the last 5 datasets
            old_datasets = Dataset.objects.order_by('-uploaded_at')[5:]
            for old_dataset in old_datasets:
                old_dataset.delete()

            return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        datasets = Dataset.objects.order_by('-uploaded_at')[:5]
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)


class DatasetDetailAPIView(APIView):
    def get(self, request, dataset_id, *args, **kwargs):
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            serializer = DatasetSerializer(dataset)
            return Response(serializer.data)
        except Dataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND)

class DownloadPDFReportAPIView(APIView):
    def get(self, request, dataset_id=None):
        try:
            if dataset_id:
                if dataset_id == 'latest':
                    dataset = Dataset.objects.latest('uploaded_at')
                else:
                    dataset = Dataset.objects.get(id=dataset_id)
            else:
                return Response({"error": "Dataset ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        except Dataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Chemical Equipment Parameter Report", styles['h1']))
        story.append(Spacer(1, 0.2 * inch))

        # Report Info
        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Dataset ID: {dataset.id}", styles['Normal']))
        story.append(Paragraph(f"File Name: {dataset.filename}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Summary Stats
        summary = dataset.summary
        story.append(Paragraph(f"Total Equipment Count: {summary.get('total_count', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Average Flowrate: {summary.get('averages', {}).get('Flowrate', 'N/A'):.2f}", styles['Normal']))
        story.append(Paragraph(f"Average Pressure: {summary.get('averages', {}).get('Pressure', 'N/A'):.2f}", styles['Normal']))
        story.append(Paragraph(f"Average Temperature: {summary.get('averages', {}).get('Temperature', 'N/A'):.2f}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Equipment Type Distribution
        story.append(Paragraph("Equipment Type Distribution:", styles['h2']))
        type_dist = summary.get('type_distribution', {})
        for eq_type, count in type_dist.items():
            percentage = (count / summary.get('total_count', 1)) * 100
            story.append(Paragraph(f"- {eq_type}: {count} ({percentage:.2f}%)", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Chart
        labels = type_dist.keys()
        sizes = type_dist.values()
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Equipment Type Distribution')

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        story.append(Image(img_buffer, width=4 * inch, height=3 * inch))

        # Footer
        # This is a bit of a hack for a footer in ReportLab
        doc.build(story)

        # Save the PDF to the model
        pdf_filename = f"report_{dataset.id}.pdf"
        buffer.seek(0)
        dataset.pdf_report.save(pdf_filename, ContentFile(buffer.read()), save=True)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        return response