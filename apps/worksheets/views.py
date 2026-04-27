from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.files.base import ContentFile
import json
import os

from .models import Worksheet, WorksheetPage, Question, Subject
from .forms import WorksheetForm, WorksheetPageForm


def _pdf_to_pages(worksheet, pdf_file):
    """
    PDF dosyasını sayfa sayfa PNG'ye çevirip her biri için WorksheetPage oluşturur.
    PyMuPDF (fitz) kullanır. Döndürülen değer: oluşturulan sayfa sayısı.
    """
    import fitz
    import io as _io

    # Dosya işaretçisini başa sar ve bytes olarak oku
    pdf_file.seek(0)
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=_io.BytesIO(pdf_bytes), filetype="pdf")
    total = len(doc)

    for i, page in enumerate(doc, 1):
        mat = fitz.Matrix(2, 2)  # ~150 DPI
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")

        wp = WorksheetPage.objects.create(
            worksheet=worksheet,
            order=i,
            page_width=pix.width,
            page_height=pix.height,
        )
        safe_pk = str(worksheet.pk).replace('-', '')
        filename = f"bg_{safe_pk}_p{i}.png"
        wp.background_image.save(filename, ContentFile(img_bytes), save=True)

    doc.close()
    return total


@login_required
def worksheet_list(request):
    worksheets = Worksheet.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'worksheets/list.html', {'worksheets': worksheets})


@login_required
def worksheet_create(request):
    if not request.user.is_teacher:
        messages.error(request, 'Sadece öğretmenler çalışma kağıdı oluşturabilir.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = WorksheetForm(request.POST, request.FILES)
        if form.is_valid():
            worksheet = form.save(commit=False)
            worksheet.author = request.user
            worksheet.save()

            pdf_file = form.cleaned_data.get('pdf_file')
            if pdf_file:
                try:
                    page_count = _pdf_to_pages(worksheet, pdf_file)
                    messages.success(
                        request,
                        f'PDF başarıyla işlendi ({page_count} sayfa). Düzenleyicide çalışabilirsiniz.'
                    )
                except Exception as e:
                    # PDF işlenemezse en az 1 boş sayfa ekle
                    WorksheetPage.objects.create(worksheet=worksheet, order=1)
                    messages.warning(
                        request,
                        f'PDF işlenirken hata oluştu, boş sayfa oluşturuldu. ({e})'
                    )
            else:
                # PDF yüklenmemişse tek boş sayfa
                WorksheetPage.objects.create(worksheet=worksheet, order=1)
                messages.success(request, 'Çalışma kağıdı oluşturuldu. Düzenleyicide çalışabilirsiniz.')

            return redirect('worksheet_editor', pk=worksheet.pk)
    else:
        form = WorksheetForm()
    return render(request, 'worksheets/create.html', {'form': form})


@login_required
def worksheet_editor(request, pk):
    worksheet = get_object_or_404(Worksheet, pk=pk, author=request.user)
    pages = worksheet.pages.prefetch_related(
        'questions__options', 'questions__drag_items',
        'questions__drop_targets', 'questions__matching_pairs',
        'embeds'
    )
    subjects = Subject.objects.all()
    return render(request, 'worksheets/editor.html', {
        'worksheet': worksheet,
        'pages': pages,
        'subjects': subjects,
        'question_types': Question.TYPE_CHOICES,
    })


def worksheet_detail(request, pk):
    worksheet = get_object_or_404(Worksheet, pk=pk)
    if not worksheet.is_public and (not request.user.is_authenticated or request.user != worksheet.author):
        messages.error(request, 'Bu çalışma kağıdına erişim izniniz yok.')
        return redirect('home')
    worksheet.view_count += 1
    worksheet.save(update_fields=['view_count'])
    return render(request, 'worksheets/detail.html', {'worksheet': worksheet})


@login_required
def worksheet_play(request, pk):
    """Öğrencinin soruları çözdüğü görünüm."""
    worksheet = get_object_or_404(Worksheet, pk=pk)
    pages = worksheet.pages.prefetch_related(
        'questions__options', 'questions__drag_items',
        'questions__drop_targets', 'questions__matching_pairs',
        'embeds'
    )
    return render(request, 'worksheets/player.html', {
        'worksheet': worksheet,
        'pages': pages,
    })


@login_required
def worksheet_delete(request, pk):
    worksheet = get_object_or_404(Worksheet, pk=pk, author=request.user)
    if request.method == 'POST':
        worksheet.delete()
        messages.success(request, 'Çalışma kağıdı silindi.')
        return redirect('worksheet_list')
    return render(request, 'worksheets/confirm_delete.html', {'worksheet': worksheet})


# ---------- API Views (JSON) ----------

@login_required
def api_page_add(request, worksheet_pk):
    worksheet = get_object_or_404(Worksheet, pk=worksheet_pk, author=request.user)
    last_order = worksheet.pages.count()
    page = WorksheetPage.objects.create(worksheet=worksheet, order=last_order + 1)
    return JsonResponse({'id': page.id, 'order': page.order})


@login_required
@require_POST
def api_page_upload_bg(request, page_pk):
    page = get_object_or_404(WorksheetPage, pk=page_pk, worksheet__author=request.user)
    if 'background_image' in request.FILES:
        page.background_image = request.FILES['background_image']
        page.save()
    return JsonResponse({'url': page.background_image.url if page.background_image else ''})


@login_required
@require_POST
def api_question_save(request, page_pk):
    page = get_object_or_404(WorksheetPage, pk=page_pk, worksheet__author=request.user)
    data = json.loads(request.body)

    with transaction.atomic():
        q_id = data.get('id')
        if q_id:
            question = get_object_or_404(Question, pk=q_id, page=page)
        else:
            question = Question(page=page)

        question.question_type = data['question_type']
        question.pos_x = data.get('pos_x', 10)
        question.pos_y = data.get('pos_y', 10)
        question.width = data.get('width', 20)
        question.height = data.get('height', 5)
        question.label = data.get('label', '')
        question.correct_answer = data.get('correct_answer', '')
        question.font_size = data.get('font_size', 14)
        question.bg_color = data.get('bg_color', '#ffffff')
        question.border_color = data.get('border_color', '#cccccc')
        question.order = data.get('order', 1)
        question.save()

        # Options (multiple_choice / dropdown)
        if 'options' in data:
            question.options.all().delete()
            for i, opt in enumerate(data['options'], 1):
                question.options.create(
                    text=opt['text'],
                    is_correct=opt.get('is_correct', False),
                    order=i
                )

        # Drag & drop items
        if 'drag_items' in data:
            question.drag_items.all().delete()
            for i, item in enumerate(data['drag_items'], 1):
                question.drag_items.create(
                    text=item['text'],
                    correct_target_id=item.get('correct_target_id', ''),
                    order=i
                )

        # Drag & drop targets
        if 'drop_targets' in data:
            question.drop_targets.all().delete()
            for t in data['drop_targets']:
                question.drop_targets.create(
                    target_id=t['target_id'],
                    label=t.get('label', ''),
                    pos_x=t.get('pos_x', 0),
                    pos_y=t.get('pos_y', 0),
                    width=t.get('width', 10),
                    height=t.get('height', 5),
                )

        # Matching pairs
        if 'matching_pairs' in data:
            question.matching_pairs.all().delete()
            for i, pair in enumerate(data['matching_pairs'], 1):
                question.matching_pairs.create(
                    left_text=pair['left_text'],
                    right_text=pair['right_text'],
                    order=i
                )

    from .serializers import QuestionSerializer
    serializer = QuestionSerializer(question)
    return JsonResponse({'success': True, 'question': serializer.data})


@login_required
@require_POST
def api_question_delete(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk, page__worksheet__author=request.user)
    question.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def api_media_embed_save(request, page_pk):
    from .models import MediaEmbed
    page = get_object_or_404(WorksheetPage, pk=page_pk, worksheet__author=request.user)
    data = json.loads(request.body)
    embed = MediaEmbed.objects.create(
        page=page,
        embed_type=data['embed_type'],
        video_url=data['video_url'],
        pos_x=data.get('pos_x', 5),
        pos_y=data.get('pos_y', 5),
        width=data.get('width', 40),
        height=data.get('height', 25),
    )
    return JsonResponse({
        'success': True,
        'id': embed.id,
        'embed_url': embed.embed_url,
        'pos_x': embed.pos_x,
        'pos_y': embed.pos_y,
        'width': embed.width,
        'height': embed.height,
    })
