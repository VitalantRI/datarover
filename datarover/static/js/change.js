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

var password = document.getElementById("new_password")
    , confirm_password = document.getElementById("confirm_new_password");

    function validatePassword(){
    let strongPassword = new RegExp('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})')
    var pass = password.value;
    if(pass.match(/[a-z]/g) && pass.match(
                /[A-Z]/g) && pass.match(
                /[0-9]/g) && pass.match(
                /[^a-zA-Z\d]/g) && pass.length >= 8){
        password.setCustomValidity('');
        // console.log("strong");
    } else {
        // console.log("too weak");
        password.setCustomValidity("Password too weak!");
    }
    
    if(password.value != confirm_password.value) {
        confirm_password.setCustomValidity("Passwords Don't Match");
    } else {
        confirm_password.setCustomValidity('');
    }
    }

new_password.onkeyup = validatePassword;
confirm_password.onkeyup = validatePassword;