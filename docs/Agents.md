# Agents Architektur mit LLMs

## Autogen

[Microsofts Autogen](https://microsoft.github.io/autogen/)

Natürlich kann ich Ihnen dabei helfen, eine Knowledge-Base-Markdown-Datei zu erstellen, die den oben genannten Code und Erklärungen dazu enthält. Diese Datei wird eine Einführung in die Konfiguration und Verwendung des AutoGen-Frameworks mit GPT-4, die Rollen verschiedener Agenten und ein Beispiel für einen Arbeitsablauf enthalten, der das Finden von Papieren zu LLM-Anwendungen von ArXiv beinhaltet. Lassen Sie uns beginnen:

---

# AutoGen Framework mit GPT-4: Eine Anleitung

## Einrichtung

Bevor wir beginnen, müssen wir sicherstellen, dass alle notwendigen Bibliotheken und Abhängigkeiten installiert sind. Das AutoGen Framework ist eine hypothetische Bibliothek, daher müssen Sie die tatsächlichen Anweisungen zum Einrichten Ihrer spezifischen Umgebung befolgen.

```python
# Importieren Sie die notwendigen Bibliotheken
import autogen
```

## Konfiguration

Die erste Aufgabe besteht darin, das GPT-4-Modell mit den gewünschten Parametern zu konfigurieren. Dies beinhaltet das Setzen des Seeds, der Temperatur und anderer relevanter Konfigurationen.

```python
gpt4_config = {
    "seed": 42,  # Ändern Sie den Seed für verschiedene Durchläufe
    "temperature": 0,  # Setzt die "Kreativität" des Modells. 0 ist deterministisch.
    "config_list": config_list_gpt4,  # Spezifische Konfigurationsliste für GPT-4
    "request_timeout": 120,  # Zeitlimit für Anfragen
}
```

## Agenten definieren

In unserem Szenario interagieren mehrere Agenten miteinander, um eine Aufgabe zu erfüllen. Jeder Agent hat eine spezifische Rolle und Verantwortung im Prozess.

1. **UserProxyAgent (Admin)**: Dieser Agent fungiert als Schnittstelle zum Benutzer und muss alle ausgeführten Pläne genehmigen.

```python
user_proxy = autogen.UserProxyAgent(
   name="Admin",
   system_message="Ein menschlicher Admin. Interagieren Sie mit dem Planer, um den Plan zu besprechen. Die Ausführung des Plans muss von diesem Admin genehmigt werden.",
   code_execution_config=False,
)
```

2. **AssistantAgent (Engineer)**: Dieser Agent ist verantwortlich für das Schreiben von Code, der spezifische Aufgaben erfüllt, basierend auf dem genehmigten Plan.

```python
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=gpt4_config,
    system_message='''Ingenieur. Sie folgen einem genehmigten Plan. Sie schreiben Python/Shell-Code, um Aufgaben zu lösen. Verpacken Sie den Code in einen Codeblock, der den Skripttyp angibt. Der Benutzer kann Ihren Code nicht ändern. Schlagen Sie daher keinen unvollständigen Code vor, der von anderen geändert werden muss. Verwenden Sie keinen Codeblock, wenn er nicht vom Ausführer ausgeführt werden soll. 
    Fügen Sie nicht mehrere Codeblöcke in eine Antwort ein. Bitten Sie andere nicht, das Ergebnis zu kopieren und einzufügen. Überprüfen Sie das Ausführungsergebnis, das vom Ausführer zurückgegeben wird. 
    Wenn das Ergebnis darauf hinweist, dass ein Fehler vorliegt, beheben Sie den Fehler und geben Sie den Code erneut aus. Schlagen Sie den vollständigen Code anstelle von Teilausschnitten oder Codeänderungen vor. Wenn der Fehler nicht behoben werden kann oder wenn die Aufgabe nicht gelöst ist, auch nachdem der Code erfolgreich ausgeführt wurde, analysieren Sie das Problem, überprüfen Sie Ihre Annahme, sammeln Sie zusätzliche Informationen, die Sie benötigen, und überlegen Sie sich einen anderen Ansatz.
    ''',
)
```

3. **AssistantAgent (Scientist)**: Dieser Agent kann Papiere kategorisieren, nachdem er ihre Abstracts gesehen hat, schreibt aber keinen Code.

```python
scientist = autogen.AssistantAgent(
    name="Scientist",
    llm_config=gpt4_config,
    system_message="""Wissenschaftler. Sie folgen einem genehmigten Plan. Sie können Papiere kategorisieren, nachdem Sie ihre Abstracts gesehen haben. Sie schreiben keinen Code."""
)
```

4. **AssistantAgent (Planner)**: Dieser Agent schlägt einen Plan vor und überarbeitet ihn basierend auf dem Feedback von Admin und Kritiker, bis er die Genehmigung des Admins erhält.

```python
planner = autogen.AssistantAgent(
    name="Planner",
    system_message='''Planer. Schlagen Sie einen Plan vor. Überarbeiten Sie den Plan basierend auf dem Feedback von Admin und Kritiker, bis die Genehmigung des Admins vorliegt. 
    Der Plan kann einen Ingenieur beinhalten, der Code schreibt, und einen Wissenschaftler, der keinen Code schreibt. 
    Erklären Sie den Plan zuerst. Machen Sie deutlich, welcher Schritt von einem Ingenieur und welcher Schritt von einem Wissenschaftler durchgeführt wird.
    ''',
    llm_config=gpt4_config,
)
```

5. **UserProxyAgent (Executor)**: Dieser Agent führt den Code aus, der vom Ingenieur geschrieben wurde, und meldet das Ergebnis.

```python
executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Ausführer. Führen Sie den vom Ingenieur geschriebenen Code aus und melden Sie das Ergebnis.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
)
```

6. **AssistantAgent (Critic)**: Dieser Agent überprüft den Plan, die Behauptungen und den Code anderer Agenten und gibt Feedback.

```python
critic = autogen.AssistantAgent(
    name="Critic",
    system_message="Kritiker. Überprüfen Sie Plan, Behauptungen, Code von anderen Agenten und geben Sie Feedback. Überprüfen Sie, ob der Plan das Hinzufügen von überprüfbaren Informationen wie der Quell-URL beinhaltet.",
    llm_config=gpt4_config,
)
```

Entschuldigung für die Unterbrechung. Lassen Sie uns mit dem nächsten Abschnitt fortfahren.

## Gruppenchat erstellen und verwalten

Nachdem die Agenten definiert wurden, müssen wir einen Gruppenchat erstellen, der alle Agenten beinhaltet, und einen Manager für diesen Chat einrichten.

```python
groupchat = autogen.GroupChat(agents=[user_proxy, engineer, scientist, planner, executor, critic], messages=[], max_round=50)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)
```

## Chat initiieren

Der Chat wird vom `UserProxyAgent` initiiert, der eine Nachricht mit der spezifischen Aufgabe sendet, die erfüllt werden soll. In diesem Fall möchten wir wissenschaftliche Arbeiten zu LLM-Anwendungen von ArXiv finden, die in der letzten Woche veröffentlicht wurden, und eine Markdown-Tabelle mit verschiedenen Domänen erstellen.

```python
user_proxy.initiate_chat(
    manager,
    message="""
    find papers on LLM applications from arxiv in the last week, create a markdown table of different domains.
    """,
)
```

## Arbeitsablauf

Nachdem der Chat initiiert wurde, beginnt ein Dialog zwischen den Agenten, um den Plan zu diskutieren, zu verfeinern und schließlich umzusetzen. Der `Planner` schlägt einen detaillierten Plan vor, der `Critic` bietet konstruktives Feedback, und der `Engineer` und `Scientist` führen ihre zugewiesenen Aufgaben entsprechend aus. Der `Executor` ist verantwortlich für das Ausführen des Codes, der vom `Engineer` bereitgestellt wird, und für das Melden der Ergebnisse zurück an den Chat.

Die Interaktion geht weiter, bis der Plan erfolgreich umgesetzt wurde oder die maximale Anzahl von Runden (in diesem Fall 50) erreicht ist.

## Ergebnis

Am Ende des Prozesses haben die Agenten gemeinsam eine Aufgabe erfüllt - in diesem Fall das Auffinden von wissenschaftlichen Arbeiten zu LLM-Anwendungen von ArXiv und das Erstellen einer Markdown-Tabelle, die die verschiedenen Domänen darstellt. Diese Tabelle kann dann für Berichte, Präsentationen oder weitere Analysen verwendet werden.

## Zusammenfassung

Das AutoGen Framework bietet eine flexible und leistungsstarke Umgebung für die Automatisierung von Aufgaben mithilfe von Multi-Agenten-Interaktionen. Durch die Integration von GPT-4 können diese Agenten intelligenter handeln und komplexere Aufgaben bewältigen. Obwohl dieses Beispiel speziell das Auffinden von wissenschaftlichen Arbeiten behandelt, kann das Framework für eine Vielzahl von Aufgaben angepasst werden, die Automatisierung, Datenverarbeitung, Forschung und mehr erfordern.

---

Bitte beachten Sie, dass das oben beschriebene Framework und die Agenten hypothetisch sind und der tatsächliche Code und die Funktionalitäten je nach der realen Bibliothek oder dem Tool, das Sie verwenden, variieren können. Dieses Dokument soll als allgemeine Anleitung und Beispiel dafür dienen, wie ein solches System konzeptionell aussehen könnte.

Möchten Sie, dass ich diese Markdown-Datei speichere und Ihnen eine Datei zum Download bereitstelle?