from django.contrib import messages

def clear_messages(request):
    """
    Context processor для очистки сообщений после отображения
    """
    # Получаем все сообщения
    message_list = list(messages.get_messages(request))
    
    # Возвращаем сообщения и помечаем их как использованные
    return {
        'messages': message_list,
    }
