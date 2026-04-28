from rest_framework import serializers
from .models import (Worksheet, WorksheetPage, Question, ChoiceOption,
                     DragDropItem, DragDropTarget, MatchingPair, MediaEmbed)


class ChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceOption
        fields = ('id', 'text', 'is_correct', 'order')


class DragDropItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DragDropItem
        fields = ('id', 'text', 'correct_target_id', 'order')


class DragDropTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DragDropTarget
        fields = ('id', 'target_id', 'label', 'pos_x', 'pos_y', 'width', 'height')


class MatchingPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingPair
        fields = ('id', 'left_text', 'right_text', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    options = ChoiceOptionSerializer(many=True, required=False)
    drag_items = DragDropItemSerializer(many=True, required=False)
    drop_targets = DragDropTargetSerializer(many=True, required=False)
    matching_pairs = MatchingPairSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'order', 'pos_x', 'pos_y', 'width', 'height',
                  'label', 'correct_answer', 'font_size', 'bg_color', 'border_color',
                  'options', 'drag_items', 'drop_targets', 'matching_pairs')

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        drag_items_data = validated_data.pop('drag_items', [])
        drop_targets_data = validated_data.pop('drop_targets', [])
        matching_pairs_data = validated_data.pop('matching_pairs', [])
        question = Question.objects.create(**validated_data)
        for opt in options_data:
            ChoiceOption.objects.create(question=question, **opt)
        for item in drag_items_data:
            DragDropItem.objects.create(question=question, **item)
        for target in drop_targets_data:
            DragDropTarget.objects.create(question=question, **target)
        for pair in matching_pairs_data:
            MatchingPair.objects.create(question=question, **pair)
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        drag_items_data = validated_data.pop('drag_items', None)
        drop_targets_data = validated_data.pop('drop_targets', None)
        matching_pairs_data = validated_data.pop('matching_pairs', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if options_data is not None:
            instance.options.all().delete()
            for opt in options_data:
                ChoiceOption.objects.create(question=instance, **opt)
        if drag_items_data is not None:
            instance.drag_items.all().delete()
            for item in drag_items_data:
                DragDropItem.objects.create(question=instance, **item)
        if drop_targets_data is not None:
            instance.drop_targets.all().delete()
            for t in drop_targets_data:
                DragDropTarget.objects.create(question=instance, **t)
        if matching_pairs_data is not None:
            instance.matching_pairs.all().delete()
            for pair in matching_pairs_data:
                MatchingPair.objects.create(question=instance, **pair)
        return instance


class MediaEmbedSerializer(serializers.ModelSerializer):
    embed_url = serializers.ReadOnlyField()

    class Meta:
        model = MediaEmbed
        fields = ('id', 'embed_type', 'video_url', 'video_id', 'embed_url',
                  'pos_x', 'pos_y', 'width', 'height')


class WorksheetPageSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    embeds = MediaEmbedSerializer(many=True, read_only=True)
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = WorksheetPage
        fields = ('id', 'order', 'background_image', 'background_image_url',
                  'page_width', 'page_height', 'audio_file', 'audio_url',
                  'text_to_speech_text', 'text_to_speech_lang',
                  'questions', 'embeds')

    def get_background_image_url(self, obj):
        if obj.background_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.background_image.url)
        return None


class WorksheetSerializer(serializers.ModelSerializer):
    pages = WorksheetPageSerializer(many=True, read_only=True)
    author_name = serializers.ReadOnlyField(source='author.full_name')

    class Meta:
        model = Worksheet
        fields = ('id', 'title', 'description', 'subject', 'level', 'language',
                  'is_public', 'thumbnail', 'tags', 'view_count', 'created_at',
                  'author_name', 'pages')
