function loadingAction() {
    $('#loading-icon').css('display', 'block');
    $('#form-inputs').fadeTo(500, 0, function() {$(this).css('visibility', 'hidden')});
}