# Documentation API

## Endpoints

### GET /
Endpoint de base pour vérifier que l'API fonctionne.

**Réponse**:
```json
{
    "msg": "Hello World"
}
```

### GET /chat
Envoie une question au chatbot.

**Paramètres**:
- `question` (string, required): La question à poser
- `conversation_id` (string, optional): ID de conversation pour maintenir le contexte

**Exemple de requête**:
```bash
curl "http://localhost:8000/chat?question=Bonjour&conversation_id=123"
```

**Réponse**:
```json
{
    "id": {
        "S": "response-uuid"
    },
    "conversation_id": {
        "S": "123"
    },
    "timestamp": {
        "S": "2024-01-20T14:30:00Z"
    },
    "question": {
        "S": "Bonjour"
    },
    "answer": {
        "S": "Bonjour! Comment puis-je vous aider aujourd'hui?"
    },
    "source": {
        "S": "api"
    }
}
```

### GET /conversations/{conversation_id}
Récupère l'historique d'une conversation spécifique.

**Paramètres**:
- `conversation_id` (string, required): ID de la conversation à récupérer

**Exemple de requête**:
```bash
curl "http://localhost:8000/conversations/123"
```

**Réponse**:
```json
{
    "messages": [
        {
            "id": "msg-uuid-1",
            "conversation_id": "123",
            "timestamp": "2024-01-20T14:30:00Z",
            "question": "Bonjour",
            "answer": "Bonjour! Comment puis-je vous aider aujourd'hui?",
            "source": "api"
        }
    ]
}
```

### POST /telegram/webhook
Endpoint pour recevoir les webhooks de Telegram.

**Corps de la requête**:
Format standard des updates Telegram.

**Réponse**:
```json
{
    "status": "ok"
}
```

## Codes d'Erreur

- `200`: Succès
- `400`: Requête invalide
- `404`: Ressource non trouvée
- `500`: Erreur serveur

## Limites et Restrictions

- Les requêtes sont limitées à 60 par minute par IP
- La taille maximale des messages est de 4096 caractères
- Les conversations sont stockées pendant 30 jours

## Authentification

Actuellement, l'API est ouverte et ne nécessite pas d'authentification. Pour la production, il est recommandé d'ajouter une authentification via:
- API Key
- JWT
- OAuth2

## Exemples d'Utilisation

### Python
```python
import requests

def ask_question(question, conversation_id=None):
    params = {
        "question": question
    }
    if conversation_id:
        params["conversation_id"] = conversation_id
    
    response = requests.get(
        "http://localhost:8000/chat",
        params=params
    )
    return response.json()
```

### JavaScript
```javascript
async function askQuestion(question, conversationId = null) {
    const params = new URLSearchParams({
        question: question
    });
    if (conversationId) {
        params.append('conversation_id', conversationId);
    }
    
    const response = await fetch(
        `http://localhost:8000/chat?${params.toString()}`
    );
    return await response.json();
}
```

## Bonnes Pratiques

1. **Gestion des Conversations**
   - Réutilisez le même `conversation_id` pour maintenir le contexte
   - Stockez le `conversation_id` côté client

2. **Gestion des Erreurs**
   - Implémentez des retries avec backoff exponentiel
   - Gérez les timeouts appropriés
   - Validez les entrées côté client

3. **Performance**
   - Mettez en cache les réponses quand c'est possible
   - Utilisez la compression gzip
   - Limitez la taille des payloads 