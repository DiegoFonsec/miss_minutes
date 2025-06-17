import os
import tempfile
import shutil
import zipfile
import csv
import subprocess
import markdown
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q

from wagtail_dp_tools.csrgenerator.meta import PLUGIN_INFO
from wagtail_dp_tools.csrgenerator.models import CSRGeneratorHistory

def csrgenerator_admin_view(request):
    # --- Leer README.md ---
    readme_html = _load_readme()

    # --- Historial y búsqueda ---
    query = request.GET.get('search', '')
    history_qs = CSRGeneratorHistory.objects.all()
    if query:
        history_qs = history_qs.filter(
            Q(project_name__icontains=query) |
            Q(common_name__icontains=query)
        )

    paginator = Paginator(history_qs.order_by('-created_at'), 4)
    page_number = request.GET.get('page')
    history_list = paginator.get_page(page_number)

    form_data = request.POST.copy()
    mode = form_data.get("mode", "generate")

    # --- Mensaje para exportación ---
    export_message = request.session.pop('export_message', None)

    # --- Exportar CSV si viene por GET ---
    if request.GET.get('export') == 'csv':
        return _export_csv(history_qs)

    # --- POST actions ---
    if request.method == 'POST':
        # Eliminar seleccionados
        if 'delete_selected' in request.POST:
            ids = request.POST.getlist('selected_ids')
            CSRGeneratorHistory.objects.filter(id__in=ids).delete()
            return redirect(f"{request.path}?tab=history")

        # Exportar seleccionados (o todo si no hay selección)
        if 'export_csv' in request.POST:
            selected_ids = request.POST.getlist('selected_ids')
            if selected_ids:
                export_qs = CSRGeneratorHistory.objects.filter(id__in=selected_ids)
            else:
                export_qs = CSRGeneratorHistory.objects.all()

            if not export_qs.exists():
                request.session['export_message'] = '⚠ No hay registros para exportar.'
                return redirect(f"{request.path}?tab=history")

            return _export_csv(export_qs)

        # Descargar ZIP de historial
        if "download_from_history" in request.POST:
            return _generate_zip_from_history(request.POST.get("download_from_history"))

        # Verificar CSR
        if mode == "verify":
            return _verify_csr(request, readme_html, form_data, history_list)

        # Confirmar y generar nuevo CSR + ZIP
        if request.POST.get("confirm") == "yes":
            return _generate_new_csr_zip(request)

        # Previsualización antes de generar
        preview = form_data.get("project_name")
        context = {
            'plugin': PLUGIN_INFO,
            'readme_html': readme_html,
            'preview': preview,
            'form_data': form_data,
            'dns_list': [d.strip() for d in form_data.get("alt_dns", "").split(",")],
            'ip_list': [ip.strip() for ip in form_data.get("alt_ips", "").split(",")] if form_data.get("use_ips") else [],
            'history_list': history_list,
            'export_message': export_message,
        }
        return render(request, 'csrgenerator/admin/csrgenerator.html', context)

    # --- GET fallback ---
    return render(request, 'csrgenerator/admin/csrgenerator.html', {
        'plugin': PLUGIN_INFO,
        'readme_html': readme_html,
        'form_data': {'mode': 'generate'},
        'history_list': history_list,
        'export_message': export_message,
    })


# ---------- Helpers ----------

def _load_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return markdown.markdown(f.read())
    return None

def _export_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="csrgenerator_history.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Usuario', 'Proyecto', 'Dominio', 'DNS SAN', 'IP SAN', 'Fecha'])

    for item in queryset:
        writer.writerow([
            item.id,
            item.user.username if item.user else '',
            item.project_name,
            item.common_name,
            item.dns_san,
            item.ip_san,
            item.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response

def _generate_zip_from_history(item_id):
    record = CSRGeneratorHistory.objects.filter(id=item_id).first()
    if not record:
        return redirect('csrgenerator_admin')

    now = datetime.now().strftime("%Y")
    folder_name = f"{record.project_name}_{now}"
    temp_dir = tempfile.mkdtemp()
    output_dir = os.path.join(temp_dir, folder_name)
    os.makedirs(output_dir)

    # Crear archivo san.cnf
    san_cnf = f"""[ req ]
default_bits = 2048
prompt = no
distinguished_name = req_distinguished_name
req_extensions = req_ext

[ req_distinguished_name ]
countryName = CO
stateOrProvinceName = Cundinamarca
localityName = Bogota
organizationalUnitName = Digital Productz MAZ
commonName = {record.common_name}

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
"""
    for i, dns in enumerate(record.dns_san.split(','), 1):
        san_cnf += f"DNS.{i} = {dns.strip()}\n"
    for i, ip in enumerate(record.ip_san.split(','), 1):
        if ip.strip():
            san_cnf += f"IP.{i} = {ip.strip()}\n"

    # Guardar y empaquetar ZIP
    san_path = os.path.join(output_dir, "san.cnf")
    with open(san_path, "w") as f:
        f.write(san_cnf)

    key_path = os.path.join(output_dir, "private.key")
    subprocess.run(["openssl", "genrsa", "-out", key_path, "2048"], check=True)

    csr_path = os.path.join(output_dir, "sslcert.csr")
    subprocess.run([
        "openssl", "req", "-new",
        "-key", key_path,
        "-out", csr_path,
        "-config", san_path
    ], check=True)

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

def _verify_csr(request, readme_html, form_data, history_list):
    csr_content = request.POST.get("csr_text", "")
    verification_output = None

    if csr_content.strip():
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_csr:
            temp_csr.write(csr_content)
            temp_csr.flush()
            temp_csr_path = temp_csr.name

        try:
            result = subprocess.run(
                ["openssl", "req", "-noout", "-text", "-in", temp_csr_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True
            )
            verification_output = result.stdout
        except subprocess.CalledProcessError as e:
            verification_output = f"❌ Error:\n{e.stdout}"
        finally:
            os.unlink(temp_csr_path)

    return render(request, 'csrgenerator/admin/csrgenerator.html', {
        'plugin': PLUGIN_INFO,
        'readme_html': readme_html,
        'form_data': form_data,
        'verification_output': verification_output,
        'history_list': history_list,
    })

def _generate_new_csr_zip(request):
    project = request.POST.get('project_name', 'Project').strip().replace(" ", "_")
    now = datetime.now().strftime("%Y")
    folder_name = f"{project}_{now}"

    temp_dir = tempfile.mkdtemp()
    output_dir = os.path.join(temp_dir, folder_name)
    os.makedirs(output_dir)

    country = request.POST.get('country', 'CO')
    state = request.POST.get('state', 'Cundinamarca')
    locality = request.POST.get('locality', 'Bogota')
    org_name = request.POST.get('org_name', '')
    org_unit = request.POST.get('org_unit', '')
    common_name = request.POST.get('common_name', '')
    email = request.POST.get('email', '')
    dns_list = request.POST.get('alt_dns', '').split(',')
    ip_list = request.POST.get('alt_ips', '').split(',') if request.POST.get('use_ips') else []

    default_bits = request.POST.get('default_bits', '2048')
    prompt = request.POST.get('prompt', 'no')
    dn_section = request.POST.get('distinguished_name', 'req_distinguished_name')
    ext_section = request.POST.get('req_extensions', 'req_ext')

    san_cnf = f"""[ req ]
default_bits = {default_bits}
prompt = {prompt}
distinguished_name = {dn_section}
req_extensions = {ext_section}

[ {dn_section} ]
countryName = {country}
stateOrProvinceName = {state}
localityName = {locality}
organizationName = {org_name}
organizationalUnitName = {org_unit}
commonName = {common_name}
"""
    if email:
        san_cnf += f"emailAddress = {email}\n"

    san_cnf += f"""

[ {ext_section} ]
subjectAltName = @alt_names

[ alt_names ]
"""
    for i, dns in enumerate(dns_list, 1):
        san_cnf += f"DNS.{i} = {dns.strip()}\n"
    for i, ip in enumerate(ip_list, 1):
        san_cnf += f"IP.{i} = {ip.strip()}\n"

    san_path = os.path.join(output_dir, "san.cnf")
    with open(san_path, "w") as f:
        f.write(san_cnf)

    key_path = os.path.join(output_dir, "private.key")
    subprocess.run(["openssl", "genrsa", "-out", key_path, default_bits], check=True)

    csr_path = os.path.join(output_dir, "sslcert.csr")
    subprocess.run([
        "openssl", "req", "-new",
        "-key", key_path,
        "-out", csr_path,
        "-config", san_path
    ], check=True)

    CSRGeneratorHistory.objects.create(
        user=request.user if request.user.is_authenticated else None,
        project_name=project,
        common_name=common_name,
        dns_san=", ".join([d.strip() for d in dns_list]),
        ip_san=", ".join([ip.strip() for ip in ip_list]),
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
