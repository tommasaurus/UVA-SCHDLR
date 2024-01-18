function addRow() {
    var table = document.getElementById("scheduleTable");
    var row = table.insertRow(-1);
    for (var i = 0; i < 3; i++) {
        var cell = row.insertCell(i);
        var textbox = document.createElement("input");
        textbox.type = "text";
        cell.appendChild(textbox);
    }
}

function removeRow() {
    var table = document.getElementById("scheduleTable");
    if (table.rows.length > 1) { // Prevents removing the header
        table.deleteRow(-1);
    }
}