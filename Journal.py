import json
import datetime as dt
import pathlib as pathlib


class Journal:
    def __init__(self, name):
        self.name = name.strip().lower()
        self.date = str(dt.date.today())
        self.jrnDict = {}
        self.CreateJournals()
        self.Load()
        if self.date not in self.jrnDict:
            self.jrnDict[self.date] = []

    def CreateJournals(self):
        path = pathlib.Path("./Journals")
        filePath = pathlib.Path(f"./Journals/jrn_{self.name}.json")
        if path.exists():
            if not filePath.exists():
                with open(filePath, 'w') as f:
                    json.dump(self.jrnDict, f)

        else:
            path.mkdir()
            with open(filePath, 'w') as f:
                json.dump(self.jrnDict, f)

    def Load(self):
        path = pathlib.Path(f"./Journals/jrn_{self.name}.json")
        with open(path) as f:
            self.jrnDict = json.load(f)

    def Save(self):
        path = pathlib.Path(f"./Journals/jrn_{self.name}.json")
        with open(path, 'w') as f:
            json.dump(self.jrnDict, f)

    def AddEntry(self, entry, time):
        if entry.split() != []:
            entry = self.CleanEntry(entry)
            self.jrnDict[self.date].append((entry, time))
            self.Save()

    def EditEntry(self, newEntry, time):
        if newEntry.split() != []:
            newEntry = self.CleanEntry(newEntry)
            self.jrnDict[self.date] = [(newEntry, time + " (Edited)")]
            self.Save()
        else:
            self.jrnDict[self.date] = []

    def GetEntries(self, key, color, mode):
        entries = ""
        if mode == "read":
            for entry, time in self.jrnDict[key]:
                entries += f'<h4 style="text-decoration: underline; color: {color}">\
                    {time}</h4>{entry}'
            return entries
        elif mode == "edit":
            for entry, time in self.jrnDict[key]:
                entries += entry.replace("<textarea>", "").replace("</textarea>", "").\
                    replace("<br>", "\n").replace("&lt;", "<").replace("&gt;", ">") + "...\n"
            return entries[:-5]

    def CleanEntry(self, entry):
        entry = entry.replace("<", "&lt;")
        entry = entry.replace(">", "&gt;")
        entry = "".join([f"<textarea>{sub}</textarea><br>" for sub in entry.split("\n")])
        return entry