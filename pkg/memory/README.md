# datasette-chatgpt-plugin

Ein Datasette-Plugin, das eine Datasette-Instanz in ein ChatGPT-Plugin verwandelt - so können Sie ChatGPT verwenden, um Fragen zu Ihren Daten zu stellen und Nachrichten in eine spezielle Tabelle einzufügen.

⚠️ **Warnung**: ChatGPT kann immer noch Ergebnisse mit diesem Plugin halluzinieren! Weitere Details zu diesem Problem finden Sie [hier](https://github.com/cutmasta-kun/datasette-chatgpt-plugin/issues/2).

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

Sobald es installiert ist, wird Ihre Datasette-Instanz mit dem neuen [ChatGPT-Plugins](https://openai.com/blog/chatgpt-plugins) System funktionieren - vorausgesetzt, Sie haben Zugang zu dieser Vorschau.

Klicken Sie auf `Plugins -> Plugin store -> Install an unverified plugin` und geben Sie die URL Ihrer Datasette-Instanz ein.

Wenn das nicht funktioniert, versuchen Sie `Develop my own plugin -> My manifest is ready` und fügen Sie dann Ihre URL ein.

ChatGPT wird das Plugin entdecken, indem es den `/.well-known/ai-plugin.json` Endpunkt aufruft.

Sie können dann Fragen stellen! Einige Startbeispiele:

- Zeige eine Liste der Tabellen (das ist immer gut, um damit zu beginnen, da es sicherstellt, dass ChatGPT weiß, welche Tabellen verfügbar sind)
- Zeige die ersten 10 Zeilen der Tabelle `mytable`
- Füge eine Nachricht zur `messages` Tabelle hinzu

Beispiel:

Angenommen, Sie haben eine Tabelle namens `users` in Ihrer Datenbank und möchten die ersten 10 Zeilen dieser Tabelle anzeigen. Sie könnten ChatGPT bitten: "Zeige die ersten 10 Zeilen der Tabelle users". ChatGPT würde dann die entsprechende Anfrage an die Datasette-Instanz senden und Ihnen das Ergebnis präsentieren.

Ebenso könnten Sie eine Nachricht zur `messages` Tabelle hinzufügen, indem Sie ChatGPT bitten: "Füge 'Hallo Welt' zur messages Tabelle hinzu". ChatGPT würde dann die entsprechende Anfrage an die Datasette-Instanz senden und Ihnen eine Bestätigung präsentieren, dass die Nachricht erfolgreich hinzugefügt wurde.
