from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .models import Page, Index, User
from .serializers import PageSerializer, UserSerializer
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required

def search_page(request):
    return render(request, "search_app/search.html")

def register_page(request):
    return render(request, "search_app/register.html")

def login_page(request):
    return render(request, "search_app/login.html")

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class SearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        sort_option = request.GET.get('sort', 'rank_desc')  # Default sorting

        if not query:
            return Response({'error': 'No query provided!'}, status=status.HTTP_400_BAD_REQUEST)

        words = query.split()

        if len(words) == 1:
            # Single-word Search
            index_entries = Index.objects.filter(keyword=words[0])
            page_ids = index_entries.values_list('page_id', flat=True).distinct()
        else:
            # Multi-word Search
            index_entries = Index.objects.filter(keyword__in=words)
            grouped = defaultdict(list)

            for entry in index_entries:
                grouped.setdefault(entry.page_id, []).append((entry.keyword, entry.position))
            
            matched_pages = []
            for page_id, tokens in grouped.items():
                tokens.sort(key=lambda x: x[1])
                positions = defaultdict(list)

                for word, position in tokens:
                    positions[word].append(position)

                phrase_found = False
                for start_position in positions[words[0]]:
                    phrase_found = True
                    for i in range(1, len(words)):
                        if start_position + i not in positions[words[i]]:
                            phrase_found = False
                            break
                    if phrase_found:
                        matched_pages.append(page_id)
                        break
            
            page_ids = set(matched_pages)

        # Apply sorting
        if sort_option == 'rank_asc':
            pages = Page.objects.filter(id__in=page_ids).order_by('rank')
        elif sort_option == 'rank_desc':
            pages = Page.objects.filter(id__in=page_ids).order_by('-rank')
        else:
            # No sorting or random sorting
            pages = Page.objects.filter(id__in=page_ids)

        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)


