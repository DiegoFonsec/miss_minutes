import tempfile
import shutil
import os
import subprocess
import zipfile
from datetime import datetime
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from wagtail_dp_tools.csrgenerator.models import CSRGeneratorHistory
from wagtail_dp_tools.csrgenerator.api.serializers import (
    CSRGeneratorHistorySerializer,
    CSRGeneratorCreateSerializer
)

class CSRGeneratorHistoryListView(generics.ListAPIView):
    serializer_class = CSRGeneratorHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        return CSRGeneratorHistory.objects.filter(user__username=username).order_by('-created_at')

class CSRGeneratorCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CSRGeneratorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        project = data['project_name'].strip().replace(" ", "_")
        now = datetime.now().strftime("%Y")
        folder_name = f"{project}_{now}"

        temp_dir = tempfile.mkdtemp()
        output_dir = os.path.join(temp_dir, folder_name)
        os.makedirs(output_dir)

        san_cnf = f"""[ req ]
default_bits = {data['default_bits']}
prompt = {data['prompt']}
distinguished_name = {data['distinguished_name']}
req_extensions = {data['req_extensions']}

[ {data['distinguished_name']} ]
countryName = {data['country']}
stateOrProvinceName = {data['state']}
localityName = {data['locality']}
organizationName = {data['org_name']}
organizationalUnitName = {data['org_unit']}
commonName = {data['common_name']}
"""
        if data.get('email'):
            san_cnf += f"emailAddress = {data['email']}\n"

        san_cnf += f"""

[ {data['req_extensions']} ]
subjectAltName = @alt_names

[ alt_names ]
"""
        for i, dns in enumerate(data.get('alt_dns', '').split(','), 1):
            if dns.strip():
                san_cnf += f"DNS.{i} = {dns.strip()}\n"
        if data.get('use_ips'):
            for i, ip in enumerate(data.get('alt_ips', '').split(','), 1):
                if ip.strip():
                    san_cnf += f"IP.{i} = {ip.strip()}\n"

        san_path = os.path.join(output_dir, "san.cnf")
        with open(san_path, "w") as f:
            f.write(san_cnf)

        key_path = os.path.join(output_dir, "private.key")
        subprocess.run(["openssl", "genrsa", "-out", key_path, str(data['default_bits'])], check=True)

        csr_path = os.path.join(output_dir, "sslcert.csr")
        subprocess.run([
            "openssl", "req", "-new",
            "-key", key_path,
            "-out", csr_path,
            "-config", san_path
        ], check=True)

        CSRGeneratorHistory.objects.create(
            user=request.user,
            project_name=project,
            common_name=data['common_name'],
            dns_san=", ".join([d.strip() for d in data.get('alt_dns', '').split(',')]),
            ip_san=", ".join([ip.strip() for ip in data.get('alt_ips', '').split(',')]) if data.get('use_ips') else '',
        )

        zip_buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        with zipfile.ZipFile(zip_buffer.name, 'w') as zipf:
            for fname in ["san.cnf", "private.key", "sslcert.csr"]:
                zipf.write(os.path.join(output_dir, fname), arcname=f"{folder_name}/{fname}")

        with open(zip_buffer.name, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{folder_name}.zip"'

        shutil.rmtree(temp_dir)
        os.unlink(zip_buffer.name)

        return response
