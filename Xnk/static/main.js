var keyTimer;
function myFunction () {
$('[id="entry"]').keyup(function () {
    var number = $(this).attr('number');
    if(keyTimer){
        clearTimeout(keyTimer);
    }
    keyTimer = setTimeout(function () {
    const form = document.getElementById('growthbook');
    const formData = new FormData(form);
    const values = [...formData.entries()];
    var time = values[2*number][1];
    var entry = values[2*number+1][1];
    var data = [
        {"time": time},
        {"entry": entry}
        ];
    document.getElementById("notify").style.color='#ff0000';
    $.ajax({
            type: "POST",
            url: '/update_book',
            data: JSON.stringify(data),
            contentType: "application/json",
            dataType: "json"
    });
    document.getElementById("notify").style.color='#00ff00';
    }, 800);
    document.getElementById("notify").style.color='#000000';
});}

$( document ).ready(function() {
    $('#myform input[type=checkbox]').on('change', function(event) {
        $('#myform').submit();
    });
    for (let i = 0; i < 33; i++){
        var id1 = 'option1_' + i;
        var id2 = 'option2_' + i;
        var id3 = 'option3_' + i;
    if (Cookies.get('state'+id1) && document.URL.includes("growth_book")) {
        document.getElementById(id1).checked=true;}
        else if (Cookies.get('state'+id2) && document.URL.includes("growth_book")) {
        document.getElementById(id2).checked=true;}
        else if (Cookies.get('state'+id3) && document.URL.includes("growth_book")) {
        document.getElementById(id3).checked=true;}

    };

});

function myWork(element) {
    var id = element.id;
    var secondPart = getSecondPart(id);
    if (id.includes('option1')) { 
        document.getElementById('option2_'+secondPart).checked = false;
        document.getElementById('option3_'+secondPart).checked = false;
        Cookies.remove('stateoption2_'+secondPart); 
        Cookies.remove('stateoption3_'+secondPart);
    }
    else if (id.includes('option2')){
                document.getElementById('option1_'+secondPart).checked = false;
        document.getElementById('option3_'+secondPart).checked = false;
        Cookies.remove('stateoption1_'+secondPart);
        Cookies.remove('stateoption3_'+secondPart);
    }
    else if (id.includes('option3')){
                document.getElementById('option1_'+secondPart).checked = false;
        document.getElementById('option2_'+secondPart).checked = false;

        Cookies.remove('stateoption1_'+secondPart);
        Cookies.remove('stateoption2_'+secondPart);
    }
    var option = document.getElementById(id);
    var number = element.getAttribute('number');
    const form = document.getElementById('worktype')
    const formData = new FormData(form);
    const values = [...formData.entries()];
    var data = [{ "worktype": values[number][1] }];
    console.log("Work Type Working")
    $.ajax({
            type: "POST",
            url: '/work_type',
            data: JSON.stringify(data),
            contentType: "application/json",
            dataType: "json"
    });
    Cookies.set('state'+id, option.checked, { expires: 1, path: '/' });
};

function getSecondPart(str) {
    return str.split('_')[1];
}
