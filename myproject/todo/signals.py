# todo/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Todo
from .serializers import TodoSerializer

@receiver(post_save, sender=Todo)
def todo_post_save(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    action = 'created' if created else 'updated'
    serializer = TodoSerializer(instance)
    async_to_sync(channel_layer.group_send)(
        'todo_updates',
        {
            'type': 'send_todo_update',   
            'action': action,
            'todo': serializer.data
        }
    )

@receiver(post_delete, sender=Todo)
def todo_post_delete(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'todo_updates',
        {
            'type': 'send_todo_update',
            'action': 'deleted',
            'todo': {'id': instance.id}
        }
    )