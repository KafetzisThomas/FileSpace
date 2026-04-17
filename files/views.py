from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import FileResponse, Http404
from .models import File

@login_required
def drive(request):
    files = File.objects.filter(owner=request.user).order_by("full_path")

    tree = {}
    for file in files:
        parts = file.full_path.split("/")
        current = tree
        for k, v in enumerate(parts):
            if k == len(parts) - 1:
                current.setdefault(v, {"_file": file})
            else:
                current = current.setdefault(v, {})

    def flatten(node, depth=0):
        items = []
        for name, value in node.items():
            is_file = "_file" in value
            items.append({
                "name": name,
                "depth": depth,
                "is_file": is_file,
                "file": value.get("_file") if is_file else None
            })
            if not is_file:
                items.extend(flatten(value, depth + 1))

        return items

    items = flatten(tree)

    return render(request, "files/drive.html", {"items": items})

@login_required
@require_POST
def upload_files(request):
    files = request.FILES.getlist('file_field')
    for file in files:
        File.objects.create(file=file, name=file.name, full_path=file.name, size=file.size, owner=request.user)
    return redirect("files:drive")

@login_required
@require_POST
def upload_dir(request):
    files = request.FILES.getlist('file_field')
    paths = request.POST.getlist('paths')
    for uploaded_file, relative_path in zip(files, paths):
        File.objects.create(file=uploaded_file, name=uploaded_file.name, full_path=relative_path, size=uploaded_file.size, owner=request.user)
    return redirect("files:drive")

@login_required
def download(request, pk):
    file = File.objects.get(pk=pk, owner=request.user)
    if not file.file:
        raise Http404()

    response = FileResponse(file.file.open(), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{file.name}"'
    return response

@login_required
@require_POST
def delete(request, pk):
    file = get_object_or_404(File, pk=pk, owner=request.user)
    file.file.delete()  # delete actual file from storage
    file.delete()  # delete db record
    return redirect("files:drive")
