function ShowDiv(){
    document.querySelector("form").onsubmit = function() {
        document.querySelector("#solving").style.display = "block";
    };
}

function OneDigit(){
    let inputs = Array.from(document.querySelectorAll("input")).filter( item => item.id !== "b");
    
    inputs.forEach(function(input){
        $(input).on('keydown keyup change', function(e){
            if (($(this).val().length === 1 && e.keyCode !== 46 && e.keyCode !== 8) || 
            ($(this).val().length === 0 && e.keyCode === 48) || 
            ($(this).val().length === 0 && e.keyCode === 189)){
                e.preventDefault();
            }   
        });
    });
}


document.addEventListener('DOMContentLoaded', function() {

    ShowDiv();
    OneDigit();
      
});
    