function textExporter(thisObj) {
    // Глобальні змінні
    var myComp;
    var myFile;
    var myProj = new File(app.project.file);
    if (myProj != null) {
        myProj = File.decode(myProj);
        myProj = myProj.split("/");
        myProj = myProj[myProj.length - 1];
    } else {
        myProj = "untitled";
    }

    // Ім'я файлу
    var nullName = (myProj !== "untitled" && myProj !== "null") 
        ? myProj.slice(0, myProj.length - 4) + ".xml" 
        : "untitled.xml";

    var saveDlg = "Save *.xml file";
    var openDlg = "Open *.xml file";
    var defaultName = $.os.match(/Windows/) ? "/Desktop/" + nullName : "~/Desktop/" + nullName;
    var extension = "eXtensible Markup Language file:*.xml";

    // Запуск UI
    var myPalette = UI(thisObj);
    if (myPalette != null && myPalette instanceof Window) {
        myPalette.show();
    }

    function UI(thisObj) {
        var main = (thisObj instanceof Panel) ? thisObj : new Window("palette", "textExporter", undefined, { resizeable: true });
        if (main != null) {
            main.preferredSize = [185, ""];
            main.margins = 15;
            var pal = main.add("group");
            pal.preferredSize = [185, ""];
            pal.orientation = "column";

            var textGroup = pal.add("panel", undefined, "Export text layers");
            textGroup.alignment = "fill";
            textGroup.alignChildren = ["left", "bottom"];
            var renderText = textGroup.add("statictext", undefined, 'Select Folder with compositions from "Project" palette');
            var exportButton = textGroup.add("button", undefined, "Export text");
            exportButton.helpTip = "Exports all text layers as a .xml file.";
            var importButton = textGroup.add("button", undefined, "Import text");
            importButton.helpTip = "Imports text from a .xml file.";

            exportButton.onClick = function () {
                myComp = app.project.activeItem;
                if (myComp != null && myComp instanceof FolderItem && myComp.numItems > 0) {
                    exportAsXML();
                } else {
                    alert("Error selecting a folder.");
                }
            };

            importButton.onClick = function () {
                myComp = app.project.activeItem;
                if (myComp != null && myComp instanceof FolderItem && myComp.numItems > 0) {
                    importXML();
                } else {
                    alert("Error selecting a folder.");
                }
            };

            main.layout.layout(true);
            main.layout.resize();
            main.onResizing = main.onResize = function () { this.layout.resize(); };
        }
        return main;
    }

    function exportAsXML() {
        var xmlFile = new File(defaultName);
        myFile = xmlFile.saveDlg(saveDlg, extension);
        if (myFile != null) {
            myFile.open("w");
            myFile.encoding = "UTF-8";
            writeXML(myComp);
            myFile.close();
        }
    }

    function writeXML(selectedComp) {
        var xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>';
        myFile.writeln(xmlHeader);
        myFile.writeln('<project name="' + myProj.slice(0, myProj.length - 4) + '">');

        for (var i = 1; i <= selectedComp.numItems; i++) {
            writeXMLnodes(selectedComp.item(i));
        }

        myFile.writeln('</project>');
    }

    function writeXMLnodes(selectedComp) {
        for (var i = 1; i <= selectedComp.numLayers; i++) {
            if (selectedComp.layer(i).source instanceof CompItem && selectedComp.layer(i).enabled) {
                writeXMLnodes(selectedComp.layer(i).source);
            } else if (selectedComp.layer(i) instanceof TextLayer && selectedComp.layer(i).enabled) {
                var composition = new XML('<composition/>');
                composition.@name = selectedComp.name;
                var layer = new XML('<layer/>');
                layer.@name = selectedComp.layer(i).name;
                var layerText = selectedComp.layer(i).sourceText.value.text.replace(/[\x00-\x1F\x7F-\x9F]/g, " ");
                layer.appendChild(layerText);
                composition.appendChild(layer);
                myFile.writeln(composition.toXMLString());
            }
        }
    }

    function importXML() {
        var tempFile = new File(defaultName);
        myFile = tempFile.openDlg(openDlg, extension);
        if (myFile != null) {
            myFile.open("r");
            readXML(myComp);
            myFile.close();
        }
    }

    function readXML(selectedComp) {
        var xmlProject = new XML(myFile.read());
        xmlProject.normalize();
        for (var i = 1; i <= selectedComp.numItems; i++) {
            insertTextFromXML(selectedComp.item(i), xmlProject);
        }
    }

    function insertTextFromXML(selectedComp, xmlProject) {
        for (var i = 1; i <= selectedComp.numLayers; i++) {
            if (selectedComp.layer(i).source instanceof CompItem && selectedComp.layer(i).enabled) {
                insertTextFromXML(selectedComp.layer(i).source, xmlProject);
            } else if (selectedComp.layer(i) instanceof TextLayer && selectedComp.layer(i).enabled) {
                for (var j = 0; j < xmlProject.elements().length(); j++) {
                    if (selectedComp.name == xmlProject.child(j).@name && selectedComp.layer(i).name == xmlProject.child(j).layer.@name) {
                        selectedComp.layer(i).sourceText.setValue(xmlProject.child(j).layer.toString());
                        break;
                    }
                }
            }
        }
    }
}

textExporter(this);