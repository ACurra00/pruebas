function carnet_x_Tipo(){
    tipoPersona = document.getElementById("tipoBuscarCarnet");
    if(tipoPersona.disabled== false){
        if(tipoPersona.selectedIndex == 0){
            console.log("Se selecciono (0) se debe Habilitar 4");
            // no se ha seleccionado nada
            document.getElementById("student_year").disabled = true;
            document.getElementById("student_year").value = "Seleccione";
            
        }else if(tipoPersona.selectedIndex == 1){
            console.log("Se selecciono (1) se debe deshabilitar 4");
           // se seleciono el estudiante
           document.getElementById("student_year").disabled = false;
           
        }else if(tipoPersona.selectedIndex == 2){
            console.log("Se selecciono (2) se debe deshabilitar 4");
           // se selecciono al docente
           document.getElementById("student_year").disabled = true;
           document.getElementById("student_year").value = "Seleccione";
        }else if(tipoPersona.selectedIndex == 3){
            console.log("Se selecciono (3) se debe deshabilitar 4");
            document.getElementById("student_year").disabled = true;
            document.getElementById("student_year").value = "Seleccione";
           // se selecciono al no docente
        }
    }     
}

function carnet_x_lotes(){
    tipoPersona = document.getElementById("tipoBuscarPersona");
    if(tipoPersona.disabled== false){
        if(tipoPersona.selectedIndex == 1){
            console.log("Se selecciono (NO) se debe Habilitar 4");
            document.getElementById("ciBuscarPersona").disabled = false;
            document.getElementById("student_year").value = "Seleccione";
            document.getElementById("tipoBuscarCarnet").value = "Seleccione";
            document.getElementById("student_year").disabled = true;
            document.getElementById("tipoBuscarCarnet").disabled = true;
            document.getElementById("id_label_ci").disabled = false;
            document.getElementById("carnet_x_lotes").disabled = true;
            
        }else if(tipoPersona.selectedIndex == 0){
            console.log("Se selecciono (SI) se debe deshabilitar 4");
            document.getElementById("ciBuscarPersona").disabled = true;
            document.getElementById("ciBuscarPersona").value = "";
            document.getElementById("student_year").value = "Seleccione";
            document.getElementById("tipoBuscarCarnet").value = "Seleccione";
            document.getElementById("student_year").disabled = true;
            document.getElementById("tipoBuscarCarnet").disabled = false;
            document.getElementById("carnet_x_lotes").disabled = false;
            document.getElementById("id_label_ci").disabled = true;  
           
        }

    }
}


function showNotification() {
    console.log("estoy aqui todo bien")
    if ("Notification" in window) {
        if (Notification.permission !== "granted" && Notification.permission !== "denied") {
            Notification.requestPermission().then(function (permission) {
                if (permission === "granted") {
                    console.log("Permiso para mostrar notificaciones concedido.");
                }
            });
        }
    }
    window.onload = function() {
        var respuesta = confirm("¿Estás seguro de que quieres hacer esto?");
        if (respuesta == true) {
            alert("Haz aceptado el mensaje.");
        } else {
            alert("Haz rechazado el mensaje.");
        }
    };
}
function showLoading() {
    document.getElementById("loading").style.display = "block";
}
function showLoadingBuscar() {
    document.getElementById("loading_busqueda").style.display = "block";
}
function hideLoading() {
    document.getElementById("loading").style.display = "none";
}
function SeleccionarTodo(){
    console.log("entro al seleccionar todo")
    console.log(document.getElementById("seleccionar_todo"))
    if(document.getElementById("seleccionar_todo")){
        console.log("ya esta en el if de seleccionar todo")
        var checkboxlist = document.getElementsByClassName("Checklist")
        console.log(checkboxlist.length)
        for (var i = 0; i < checkboxlist.length; i++){
            console.log("for")
            console.log(checkboxlist[i])
            checkboxlist[i].checked = true
        }
    }
}
