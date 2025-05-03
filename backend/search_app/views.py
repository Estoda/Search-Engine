from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Page
from .serializers import PageSerializer
from django.db.models import Q

class SearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({'error': 'No query provided!'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = Page.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by('-rank')[:20]
        serializer = PageSerializer(results, many=True)
        return Response(serializer.data)