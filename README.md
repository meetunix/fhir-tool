# FHIR-Tools

## fhir-tool.py - Massenimport und Ressourcenanzahl

Python-Skript zum Massenimport von Ressourcen auf einen FHIR-Server und zur
Anzeige, wie viele Ressourcen eines Typs auf einem FHIR-Server gespeichert sind.

**Features:**

1. Import einer Ressource (einzelne json-Datei) oder Massenimport vieler Ressourcen, die sich als
json-Datei alle in einem Verzeichnis befinden.
2. HTTPS wird unterstützt, eine Prüfung des Serverzertifikates findet
allerdings nicht statt. Damit werden auch selbst signierte Zertifikate unkompliziert unterstützt.
3. BasicAuth wird unterstützt.


### Abhängigkeiten

- Python 3.7
- extern
  - python-requests

`$ pip install -r requirements.txt`

### Verwendung

Der REST-Endpoint `-b |--base-path <URL>` muss bei jeder Aktion angegeben werden. Wird HTTP
Basic-Authentication genutzt, muss zusätzlich die option
`-a | --basic-authentication <USERNAME>:<PASSWORD>` verwendet werden.

**Zusammenfassung: Ressourcenanzahl auf einem Server**

`-s | --summary`

Das Skript prüft welche Ressourcen der FHIR-Server unterstützt und erfragt über einzelne
FHIR-Search-Anfragen die Anzahl dieser Ressourcen und gibt sie sortiert aus.

Beispiel:
```
$ python3 fhir-tool.py -b http://fhir-server:8080/fhir -s

17    Medication
44    MedicationStatement
312   Patient
1629  Encounter
4212  Procedure
4901  Condition
21606 Observation
```
**(Massen)import von FHIR-Ressourcen**

`-r | --resource-directory <PATH>`

Import einer einzelnen Datei oder eines ganzen Verzeichnisses. Die Ressourcen müssen als
json-Datei vorliegen.

Beispiel für Einzelimport:

```
$ python3 fhir-tool.py -b http://fhir-server:8080/fhir \
-r /path/to/resource.json
```

Beispiel für Massenimport:
```
$ python3 fhir-tool.py -b http://fhir-server:8080/fhir \
-r /path/to/resources/ \
-a user001:verySecReT
```

## Weitere geplante Werkzeuge

1. FHIR-Graph: Erstellung eines Abhängigkeitsgraphen in Bezug zu einer FHIR-Ressource
(z.B. Alle Ressourcen die direkt und indirekt von einem Patienten abhängen). Inklusiver grafischer
Repräsentation.



