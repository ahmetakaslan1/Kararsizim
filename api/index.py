import os
import sys

# Vercel'in Python runtime'ı dosyaları kök dizinden okur.
# Django projesi 'backend' klasörünün içinde olduğu için
# Python'un 'backend' klasörünü modül olarak görebilmesi için sys.path'e ekliyoruz.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kararsiz_backend.settings')

# Vercel Serverless Function için "app" değişkeni gereklidir.
app = get_wsgi_application()
