from django.shortcuts import render
import numpy as np
from django.shortcuts import render, redirect
from .forms import RecordForm, QueryVectorForm, TextSearchForm
from .models import Record
from django.db import connection
from django.db.models import F, Value
from pgvector.django import L2Distance
from django.contrib.postgres.search import TrigramSimilarity

def index(request):
    return render(request, 'index.html')

def insert_record(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.vector = form.cleaned_data['vector']
            record.save()
            return redirect('insert_record')
    else:
        form = RecordForm()
    return render(request, 'insert_record.html', {'form': form})

def search_records_sql(request):
    results = []
    if request.method == 'POST':
        form = QueryVectorForm(request.POST)
        if form.is_valid():
            query_vector_str = form.cleaned_data['vector']
            query_vector = [float(x) for x in query_vector_str.split(',')]
            k = form.cleaned_data['k']

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, text, vector, vector <-> %s::vector AS distance
                    FROM myapp_record
                    ORDER BY distance ASC
                    LIMIT %s
                """, [query_vector, k])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return render(request, 'search_results.html', {'results': results, 'form': form})
    else:
        form = QueryVectorForm()

    return render(request, 'search_results.html', {'results': results, 'form': form})

def search_records_django(request):
    results = []
    if request.method == 'POST':
        form = QueryVectorForm(request.POST)
        if form.is_valid():
            query_vector_str = form.cleaned_data['vector']
            query_vector = [float(x) for x in query_vector_str.split(',')]
            k = form.cleaned_data['k']

            results = Record.objects.annotate(
                distance=L2Distance('vector', query_vector)
            ).order_by('distance')[:k]

    else:
        form = QueryVectorForm()

    return render(request, 'search_results.html', {'results': results, 'form': form})
    
def search_trigram(request):
    results = []
    if request.method == 'POST':
        form = TextSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']

            results = Record.objects.annotate(
                similarity=TrigramSimilarity('text', query)
            ).filter(similarity__gt=0.1).order_by('-similarity')

    else:
        form = TextSearchForm()

    return render(request, 'search_results.html', {'results': results, 'form': form})
    
