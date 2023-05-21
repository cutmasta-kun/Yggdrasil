# queue-system-chatgpt-plugin

Ein ChatGPT-Plugin, das eine generische Warteschlange für Aufgaben bereitstellt. Mit diesem Plugin können Sie Aufgaben zur Verarbeitung in eine Warteschlange stellen und den Status und das Ergebnis der Aufgaben abrufen.

## Installation

Um dieses Plugin zu installieren, folgen Sie den unten stehenden Schritten:

1. Erstellen Sie eine neue Python-Umgebung und aktivieren Sie diese:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Installieren Sie die erforderlichen Abhängigkeiten:

    ```bash
    pip install -r requirements.txt
    ```

3. Führen Sie die Hauptanwendung aus:

    ```bash
    python main.py
    ```

## Verwendung

Sobald es installiert ist, wird Ihr generisches Warteschlangensystem mit dem neuen [ChatGPT-Plugins](https://openai.com/blog/chatgpt-plugins) System funktionieren - vorausgesetzt, Sie haben Zugang zu dieser Vorschau.

Klicken Sie auf `Plugins -> Plugin store -> Install an unverified plugin` und geben Sie die URL Ihrer generischen Warteschlangensystem-Instanz ein.

Wenn das nicht funktioniert, versuchen Sie `Develop my own plugin -> My manifest is ready` und fügen Sie dann Ihre URL ein.

ChatGPT wird das Plugin entdecken, indem es den `/.well-known/ai-plugin.json` Endpunkt aufruft.

Sie können dann Aufgaben zur Verarbeitung in die Warteschlange stellen und den Status und das Ergebnis der Aufgaben abrufen. Einige Startbeispiele:

- Füge eine neue Aufgabe zur Warteschlange hinzu
- Hole den Status einer Aufgabe anhand ihrer Queue-ID
- Hole das Ergebnis einer Aufgabe anhand ihrer Queue-ID

Beispiel:

Angenommen, Sie möchten eine neue Aufgabe zur Verarbeitung in die Warteschlange stellen. Sie könnten ChatGPT bitten: "Füge eine neue Aufgabe zur Warteschlange hinzu". ChatGPT würde dann die entsprechende Anfrage an das generische Warteschlangensystem senden und Ihnen die Queue-ID der neuen Aufgabe präsentieren.

Ebenso könnten Sie den Status oder das Ergebnis einer Aufgabe abrufen, indem Sie ChatGPT bitten: "Hole den Status der Aufgabe mit der Queue-ID XYZ" oder "Hole das Ergebnis der Aufgabe mit der Queue-ID XYZ". ChatGPT würde dann die entsprechende Anfrage an das generische Warteschlangensystem senden und Ihnen den Status oder das Ergebnis der Aufgabe präsentieren.
