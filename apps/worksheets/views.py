from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.files.base import ContentFile
import json
import os
<<<<<<< HEAD
import re
=======
>>>>>>> 7770ffe167c904d7b6910d141eeaeca9600e565c

from .models import Worksheet, WorksheetPage, Question, Subject
from .forms import WorksheetForm, WorksheetPageForm


<<<<<<< HEAD
HEX_COLOR_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_hex_color(value, default):
    if isinstance(value, str) and HEX_COLOR_RE.match(value):
        return value.lower()
    return default


=======
>>>>>>> 7770ffe167c904d7b6910d141eeaeca9600e565c
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
<<<<<<< HEAD
    pages_data = {}
    for page in pages:
        page_questions = []
        for q in page.questions.all():
            page_questions.append({
                'id': q.id,
                'type': q.question_type,
                'pos_x': q.pos_x,
                'pos_y': q.pos_y,
                'width': q.width,
                'height': q.height,
                'label': q.label or '',
                'correct_answer': q.correct_answer or '',
                'font_size': q.font_size,
                'bg_color': q.bg_color,
                'border_color': q.border_color,
                'options': [
                    {'id': opt.id, 'text': opt.text, 'is_correct': opt.is_correct}
                    for opt in q.options.all()
                ],
                'drag_items': [
                    {
                        'id': item.id,
                        'text': item.text,
                        'correct_target_id': item.correct_target_id,
                    }
                    for item in q.drag_items.all()
                ],
                'matching_pairs': [
                    {
                        'id': pair.id,
                        'left_text': pair.left_text,
                        'right_text': pair.right_text,
                    }
                    for pair in q.matching_pairs.all()
                ],
            })
        pages_data[page.id] = {'questions': page_questions}

=======
>>>>>>> 7770ffe167c904d7b6910d141eeaeca9600e565c
    subjects = Subject.objects.all()
    return render(request, 'worksheets/editor.html', {
        'worksheet': worksheet,
        'pages': pages,
<<<<<<< HEAD
        'pages_data': pages_data,
=======
>>>>>>> 7770ffe167c904d7b6910d141eeaeca9600e565c
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
<<<<<<< HEAD
            question = get_object_or_404(Question, pk=q_id, page__worksheet__author=request.user)
            page = question.page
=======
            question = get_object_or_404(Question, pk=q_id, page=page)
>>>>>>> 7770ffe167c904d7b6910d141eeaeca9600e565c
        else:
            question = Question(page=page)

        question.question_type = data['question_type']
<<<<<<< HEAD
        question.pos_x = _to_float(data.get('pos_x', 10), 10)
        question.pos_y = _to_float(data.get('pos_y', 10), 10)
        question.width = _to_float(data.get('width', 20), 20)
        question.height = _to_float(data.get('height', 5), 5)
        question.label = data.get('label', '')
        question.correct_answer = data.get('correct_answer', '')
        question.font_size = max(8, min(36, _to_int(data.get('font_size', 14), 14)))
        question.bg_color = _normalize_hex_color(data.get('bg_color', '#ffffff'), '#ffffff')
        question.border_color = _normalize_hex_color(data.get('border_color', '#cccccc'), '#cccccc')
=======
        question.pos_x = data.get('pos_x', 10)
        question.pos_y = data.get('pos_y', 10)
        question.width = data.get('width', 20)
        question.height = data.get('height', 5)
        question.label = data.get('label', '')
        question.correct_answer = data.get('correct_answer', '')
        question.font_size = data.get('font_size', 14)
        question.bg_color = data.get('bg_color', '#ffffff')
        question.border_color = data.get('border_color', '#cccccc')
>>>>>>> 7770ffe167c904d7b6910d141eeaeca9600e565c
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
