# Yggdrasil

Yggdrasil ist ein flexibles und robustes System, das auf der Basis von NTFY-Nachrichten verschiedene Aktionen auslösen kann. Es ist benannt nach dem Weltenbaum aus der nordischen Mythologie, der verschiedene Bereiche des Universums verbindet.

## Hauptfunktionalitäten

1. **Informationsbeschaffung**: Yggdrasil kann an neue und unabhängige Informationen kommen. Zum Beispiel ermöglicht das Arxiv Search Plugin die Suche nach wissenschaftlichen Arbeiten auf ArXiv.

2. **Informationsspeicherung**: Yggdrasil kann Informationen speichern und abrufen. Dies wird durch den Memory Service und das Memory Interface Plugin ermöglicht, die sowohl für kurzfristige als auch für langfristige Speicheranforderungen verwendet werden können.

3. **Kommunikation**: Yggdrasil kann Benachrichtigungen an externe Systeme senden und auf spezifische NTFY-Themen hören. Dies wird durch das NTFY Plugin und den Communication Service ermöglicht.

4. **Funktionsauslösung**: Yggdrasil kann verschiedene Funktionen auslösen, basierend auf den empfangenen Nachrichten. Dies wird durch den Communication Service und den Function Service ermöglicht.

## Installation

Um Yggdrasil zu installieren, führen Sie die folgenden Befehle aus:

```bash
git clone https://github.com/cutmasta-kun/Yggdrasil.git
cd /Yggdrasil/deploy
docker compose build
docker compose up
```

## Weiterentwicklung

Yggdrasil ist ein offenes Projekt und wir freuen uns über Beiträge von der Community. Wenn Sie eine Idee für eine Verbesserung haben oder einen Fehler gefunden haben, zögern Sie bitte nicht, ein Issue zu eröffnen oder einen Pull Request zu erstellen.