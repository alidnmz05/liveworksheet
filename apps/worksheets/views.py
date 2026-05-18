from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.files.base import ContentFile
import json
import os
import re
import io as _io

try:
    import pymupdf as fitz
    _PYMUPDF_OK = True
except Exception:
    fitz = None
    _PYMUPDF_OK = False

from .models import Worksheet, WorksheetPage, Question, Subject
from .forms import WorksheetForm, WorksheetPageForm


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


def _pdf_to_pages(worksheet, pdf_file):
    """
    PDF dosyasını sayfa sayfa PNG'ye çevirip her biri için WorksheetPage oluşturur.
    PyMuPDF (fitz) kullanır. Döndürülen değer: oluşturulan sayfa sayısı.
    """
    if not _PYMUPDF_OK or fitz is None:
        raise RuntimeError("PyMuPDF yüklenemedi. Sunucuyu yeniden başlatın.")

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
    worksheets = Worksheet.objects.filter(author=request.user).prefetch_related('pages').order_by('-created_at')
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
                'points': q.points,
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
        pages_data[page.id] = {
            'questions': page_questions,
            'embeds': [
                {
                    'id': emb.id,
                    'type': 'embed',
                    'embed_type': emb.embed_type,
                    'video_url': emb.video_url,
                    'embed_url': emb.embed_url,
                    'pos_x': emb.pos_x,
                    'pos_y': emb.pos_y,
                    'width': emb.width,
                    'height': emb.height,
                }
                for emb in page.embeds.all()
            ]
        }

    subjects = Subject.objects.all()
    return render(request, 'worksheets/editor.html', {
        'worksheet': worksheet,
        'pages': pages,
        'pages_data': pages_data,
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
    assignment_id = request.GET.get('assignment')
    if not assignment_id and request.user.is_authenticated:
        from apps.assignments.models import Assignment
        pending_assignment = Assignment.objects.filter(
            worksheet=worksheet,
            classrooms__students=request.user
        ).exclude(
            submissions__student=request.user,
            submissions__is_draft=False
        ).order_by('-created_at').first()
        if pending_assignment:
            assignment_id = pending_assignment.id

    draft_answers_json = "{}"
    if request.user.is_authenticated:
        from apps.submissions.models import Submission
        import json
        if assignment_id:
            draft = Submission.objects.filter(
                student=request.user, assignment_id=assignment_id, is_draft=True
            ).first()
        else:
            draft = Submission.objects.filter(
                student=request.user, worksheet=worksheet, assignment__isnull=True, is_draft=True
            ).first()

        if draft:
            answers_dict = {}
            for ans in draft.answers.all():
                try:
                    answers_dict[str(ans.question_id)] = json.loads(ans.given_answer)
                except ValueError:
                    answers_dict[str(ans.question_id)] = ans.given_answer
            draft_answers_json = json.dumps(answers_dict)

    return render(request, 'worksheets/player.html', {
        'worksheet': worksheet,
        'pages': pages,
        'draft_answers_json': draft_answers_json,
        'assignment_id': assignment_id,
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
    import traceback as _tb
    page = get_object_or_404(WorksheetPage, pk=page_pk, worksheet__author=request.user)
    try:
        if 'background_image' in request.FILES:
            uploaded_file = request.FILES['background_image']

            fname_lower = uploaded_file.name.lower()

            # Word dosyası → önce PDF'e çevir, sonra PDF dalına düş
            if fname_lower.endswith('.docx') or fname_lower.endswith('.doc'):
                if not _PYMUPDF_OK or fitz is None:
                    return JsonResponse({'error': 'PyMuPDF yüklenemedi. Sunucuyu yeniden başlatın.'}, status=500)
                try:
                    from docx2pdf import convert as _docx2pdf
                except ImportError:
                    return JsonResponse({'error': 'docx2pdf paketi bulunamadı. pip install docx2pdf'}, status=500)
                import tempfile, shutil
                uploaded_file.seek(0)
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_in:
                    tmp_in.write(uploaded_file.read())
                    tmp_in_path = tmp_in.name
                tmp_out_path = tmp_in_path.replace('.docx', '.pdf')
                try:
                    _docx2pdf(tmp_in_path, tmp_out_path)
                    with open(tmp_out_path, 'rb') as f:
                        pdf_bytes = f.read()
                finally:
                    try: os.remove(tmp_in_path)
                    except Exception: pass
                    try: os.remove(tmp_out_path)
                    except Exception: pass
                doc = fitz.open(stream=_io.BytesIO(pdf_bytes), filetype="pdf")

            # Eğer yüklenen dosya bir PDF ise
            elif fname_lower.endswith('.pdf'):
                if not _PYMUPDF_OK or fitz is None:
                    return JsonResponse({'error': 'PyMuPDF yüklenemedi. Sunucuyu yeniden başlatın.'}, status=500)

                uploaded_file.seek(0)
                pdf_bytes = uploaded_file.read()
                doc = fitz.open(stream=_io.BytesIO(pdf_bytes), filetype="pdf")

                if len(doc) > 0:
                    # İlk sayfayı mevcut sayfaya arka plan olarak ayarla
                    pdf_page = doc[0]
                    mat = fitz.Matrix(2, 2)
                    pix = pdf_page.get_pixmap(matrix=mat, alpha=False)
                    img_bytes = pix.tobytes("png")

                    safe_pk = str(page.worksheet.pk).replace('-', '')
                    filename = f"bg_{safe_pk}_p{page.order}.png"

                    page.page_width = pix.width
                    page.page_height = pix.height
                    page.background_image.save(filename, ContentFile(img_bytes), save=True)

                    # Eğer PDF birden fazla sayfaysa, kalan sayfalar için yeni WorksheetPage oluştur
                    if len(doc) > 1:
                        worksheet = page.worksheet
                        current_order = worksheet.pages.count()
                        for i in range(1, len(doc)):
                            current_order += 1
                            pdf_page_i = doc[i]
                            pix_i = pdf_page_i.get_pixmap(matrix=mat, alpha=False)
                            img_bytes_i = pix_i.tobytes("png")

                            wp = WorksheetPage.objects.create(
                                worksheet=worksheet,
                                order=current_order,
                                page_width=pix_i.width,
                                page_height=pix_i.height,
                            )
                            fn_i = f"bg_{safe_pk}_p{current_order}.png"
                            wp.background_image.save(fn_i, ContentFile(img_bytes_i), save=True)
                doc.close()
            else:
                # Sadece bir görsel yüklendiyse (JPG, PNG vs.)
                from PIL import Image, ImageOps
                uploaded_file.seek(0)
                img_bytes_raw = uploaded_file.read()
                with Image.open(_io.BytesIO(img_bytes_raw)) as _raw_img:
                    orig_format = _raw_img.format or 'PNG'
                    img = ImageOps.exif_transpose(_raw_img)  # EXIF rotasyonunu uygula
                    orig_w, orig_h = img.width, img.height
                    max_width = 1000
                    if orig_w > max_width:
                        ratio = max_width / float(orig_w)
                        new_h = int(orig_h * ratio)
                        img_resized = img.resize((max_width, new_h), Image.Resampling.LANCZOS)
                        temp_io = _io.BytesIO()
                        img_resized.save(temp_io, format=orig_format)
                        page.background_image.save(
                            uploaded_file.name,
                            ContentFile(temp_io.getvalue()),
                            save=False,
                        )
                        page.page_width = max_width
                        page.page_height = new_h
                    else:
                        temp_io = _io.BytesIO()
                        img.save(temp_io, format=orig_format)
                        page.background_image.save(
                            uploaded_file.name,
                            ContentFile(temp_io.getvalue()),
                            save=False,
                        )
                        page.page_width = orig_w
                        page.page_height = orig_h
                page.save()

        return JsonResponse({'url': page.background_image.url if page.background_image else ''})
    except Exception as exc:
        return JsonResponse({'error': str(exc), 'traceback': _tb.format_exc()}, status=500)


@login_required
@require_POST
def api_page_delete_bg(request, page_pk):
    page = get_object_or_404(WorksheetPage, pk=page_pk, worksheet__author=request.user)
    if page.background_image:
        page.background_image.delete()
        page.page_width = 794
        page.page_height = 1123
        page.save()
    return JsonResponse({'success': True})


@login_required
@require_POST
def api_question_save(request, page_pk):
    page = get_object_or_404(WorksheetPage, pk=page_pk, worksheet__author=request.user)
    data = json.loads(request.body)

    with transaction.atomic():
        q_id = data.get('id')
        if q_id:
            question = get_object_or_404(Question, pk=q_id, page__worksheet__author=request.user)
            page = question.page
        else:
            question = Question(page=page)

        question.question_type = data['question_type']
        question.pos_x = _to_float(data.get('pos_x', 10), 10)
        question.pos_y = _to_float(data.get('pos_y', 10), 10)
        question.width = _to_float(data.get('width', 20), 20)
        question.height = _to_float(data.get('height', 5), 5)
        question.label = data.get('label', '')
        question.correct_answer = data.get('correct_answer', '')
        question.font_size = max(8, min(36, _to_int(data.get('font_size', 14), 14)))
        question.bg_color = _normalize_hex_color(data.get('bg_color', '#ffffff'), '#ffffff')
        question.border_color = _normalize_hex_color(data.get('border_color', '#cccccc'), '#cccccc')
        question.points = max(1, _to_int(data.get('points', 1), 1))
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
def api_question_duplicate(request, question_pk):
    original = get_object_or_404(Question, pk=question_pk, page__worksheet__author=request.user)
    
    with transaction.atomic():
        # Duplicate the main question object
        options = original.options.all()
        drag_items = original.drag_items.all()
        matching_pairs = original.matching_pairs.all()
        
        # New question
        new_q = Question.objects.get(pk=question_pk)
        new_q.pk = None
        # Shift slightly so it's visible that it's a copy
        new_q.pos_x = min(95.0, float(new_q.pos_x) + 2.0)
        new_q.pos_y = min(95.0, float(new_q.pos_y) + 2.0)
        new_q.save()
        
        # Duplicate related sets
        for opt in options:
            opt.pk = None
            opt.question = new_q
            opt.save()
        for item in drag_items:
            item.pk = None
            item.question = new_q
            item.save()
        for pair in matching_pairs:
            pair.pk = None
            pair.question = new_q
            pair.save()
            
    from .serializers import QuestionSerializer
    serializer = QuestionSerializer(new_q)
    return JsonResponse({'success': True, 'question': serializer.data})


@login_required
@require_POST
def api_media_embed_save(request, page_pk):
    from .models import MediaEmbed
    page = get_object_or_404(WorksheetPage, pk=page_pk, worksheet__author=request.user)
    data = json.loads(request.body)
    
    embed_id = data.get('id')
    if embed_id:
        embed = get_object_or_404(MediaEmbed, pk=embed_id, page__worksheet__author=request.user)
        if 'video_url' in data: embed.video_url = data['video_url']
        if 'embed_type' in data: embed.embed_type = data['embed_type']
        if 'pos_x' in data: embed.pos_x = _to_float(data['pos_x'], embed.pos_x)
        if 'pos_y' in data: embed.pos_y = _to_float(data['pos_y'], embed.pos_y)
        if 'width' in data: embed.width = _to_float(data['width'], embed.width)
        if 'height' in data: embed.height = _to_float(data['height'], embed.height)
        embed.save()
    else:
        embed = MediaEmbed.objects.create(
            page=page,
            embed_type=data.get('embed_type', 'youtube'),
            video_url=data.get('video_url', ''),
            pos_x=_to_float(data.get('pos_x', 5), 5),
            pos_y=_to_float(data.get('pos_y', 5), 5),
            width=_to_float(data.get('width', 40), 40),
            height=_to_float(data.get('height', 25), 25),
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


@login_required
@require_POST
def api_media_embed_delete(request, embed_pk):
    from .models import MediaEmbed
    embed = get_object_or_404(MediaEmbed, pk=embed_pk, page__worksheet__author=request.user)
    embed.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def api_media_embed_duplicate(request, embed_pk):
    from .models import MediaEmbed
    original = get_object_or_404(MediaEmbed, pk=embed_pk, page__worksheet__author=request.user)
    
    new_embed = MediaEmbed.objects.get(pk=embed_pk)
    new_embed.pk = None
    new_embed.pos_x = min(90.0, float(new_embed.pos_x) + 3.0)
    new_embed.pos_y = min(90.0, float(new_embed.pos_y) + 3.0)
    new_embed.save()
    
    return JsonResponse({
        'success': True,
        'id': new_embed.id,
        'embed_url': new_embed.embed_url,
        'pos_x': new_embed.pos_x,
        'pos_y': new_embed.pos_y,
        'width': new_embed.width,
        'height': new_embed.height,
    })


@login_required
@require_POST
def ai_tutor_query(request):
    """Yapay Zeka Asistanı için çalışma kağıtları önerir."""
    from django.db.models import Q
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz veri formatı.'}, status=400)

    level = data.get('level', '').strip()
    topic = data.get('topic', '').strip()

    query = Q(is_public=True)
    if level:
        query &= Q(level__iexact=level)
    if topic:
        query &= (
            Q(title__icontains=topic) |
            Q(description__icontains=topic) |
            Q(tags__icontains=topic) |
            Q(subject__name__icontains=topic)
        )

    results = Worksheet.objects.filter(query).select_related('subject', 'author')[:5]

    worksheets_data = []
    for ws in results:
        worksheets_data.append({
            'id': str(ws.id),
            'title': ws.title,
            'subject': ws.subject.name if ws.subject else 'Genel',
            'author': ws.author.full_name,
            'question_count': ws.question_count,
            'thumbnail': ws.thumbnail.url if ws.thumbnail else None,
            'url': f"/worksheets/{ws.id}/play/"
        })

    return JsonResponse({'success': True, 'worksheets': worksheets_data})
