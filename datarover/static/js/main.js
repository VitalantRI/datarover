// Data Rover
// Copyright (C) 2022  Vitalant
// Developed by Vincent Chiang

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

// $(function(){

//    var requiredCheckboxes = $(':checkbox[required]');

//    requiredCheckboxes.change(function(){

//       if(requiredCheckboxes.is(':checked')) {
//          requiredCheckboxes.removeAttr('required');
//       }

//       else {
//          requiredCheckboxes.attr('required', 'required');
//       }
//    });

//    });

function changeAction(val) {
    document.forms[0].action = val;
}

var tNumber = 1;
// console.log(relations)

function setKeys(s){
if ("1" == s){
    return false
}
var table = document.getElementById("t" + s);
var key = document.getElementById("k" + s);

// console.log(key);
// console.log(table.selectedIndex);
var tVal = table.options[table.selectedIndex].value;
// console.log(tVal);
if (tVal == ""){
    return false
}
key.innerHTML = "";
var cands = relations[tVal];
// console.log(cands);
let n = parseInt(s);
for (var i = 0; i < n ; i ++){
    if (i == 0){
        var temp = document.createElement("option");
        temp.value = "";
        temp.text = "--Please choose join keys--";
        key.append(temp)
    }
    else{
        var tempt = document.getElementById("t" + String(i));;
        var val = tempt.value;


        if (val in cands){
            possibles = cands[val]
            // console.log(possibles)
            for (const pairs of possibles){
            console.log(pairs)
            var temp = document.createElement("option");
            temp.value = pairs;
            temp.text = pairs;
            key.append(temp)
            }
        }
    }
}
return true
}

function createJoin (){
var joinT = document.createElement("select");
joinT.name = "joinT";
var arr = ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"];
for (var i = 0; i < arr.length; i++){
    var temp = document.createElement("option");
    temp.value = arr[i];
    temp.text = arr[i];
    joinT.appendChild(temp);
    }
return joinT
}

function createJoinK(){
var joinK =document.createElement("select");
joinK.name = "joinK"
joinK.id = "k" + String(tNumber);
var temp = document.createElement("option");
temp.value = "";
temp.text = "--Please choose join keys--";
joinK.required = true;

joinK.appendChild(temp);

return joinK
}

function removeDups(){
var selectedValues = [];
$('.tName').each(function() {
    var thisValue = this.value;
    if(thisValue !== '')
        selectedValues.push(thisValue);
}).each(function() {
    $(this).find('option:not(:selected)').each(function() {
        if( $.inArray( this.value, selectedValues ) === -1 ) {
        $(this).removeAttr('hidden');
        } else {
        if(this.value !== '')
            $(this).attr('hidden', 'hidden');
        }
    });
});
}

$(".add").click(function() {
tNumber ++;
var temp = $("#t_select > p:first-child").clone(true);
var button = document.createElement("BUTTON");
button.setAttribute("class", "remove");
button.innerHTML = "Remove";
button.addEventListener("click", function() {
    $(this).parent().remove();
    tNumber --;
    return false;
})
var tableselect = temp.children()[0];
tableselect.id = "t" + String(tNumber);
// tableselect.onchange = function(){
//    // var keySelect = $('#k' + String(tNumber));
//    // var temp = document.createElement("option");
//    // var options = key_helper()
    
//    // keySelect.append(temp);
//    setKeys(this.id[1]);
// }
temp.append(createJoinK());

temp.append(button);
    
temp.prepend(createJoin());

temp.insertBefore("#t_select > p:last-child");

removeDups();
return false;
});

/* $(".remove").click(function() {
$(this).parent().remove();
return false;
}); */

$('.tName').change(function() {
removeDups();
var index = parseInt(this.id[1]);
for (var i = index; i <= tNumber; i ++){
    setKeys(String(i));
}
}).trigger('change'); // run at load